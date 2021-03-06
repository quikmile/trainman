# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields.array import ArrayField
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from ..base.models import BaseModel, BaseNode
from ..custom.gitlab.project_apis import GitlabProject

SERVER_TYPES = (('STAG', 'Staging'),
                ('PROD', 'Production'))

DATABASE_SERVER = (('On Service Host', 'On Service Host'),
                   ('Remote Host', 'Remote Host'))

HTTP_SERVER = (('NGINX', 'NGINX'),)
DEFAULT_HTTP_PORT = 8000
DEFAULT_TCP_PORT = 8001


class Service(BaseModel):
    service_name = models.CharField(max_length=100, unique=True)
    repo_url = models.CharField(max_length=100, unique=True)
    gitlab_project_id = models.IntegerField(unique=True)
    contributors = ArrayField(models.CharField(max_length=300), null=True, blank=True)

    smtp_server = models.ForeignKey('servers.SMTPServer', null=True, blank=True)
    http_server = models.CharField(choices=HTTP_SERVER, max_length=20, default='NGINX')
    service_uri = models.CharField(max_length=100, unique=True)

    # class Meta:
    #     unique_together = ('database_id', 'content_object')
    def save(self, *args, **kwargs):
        super(Service, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{}'.format(self.service_name)

    # def get_database(self):
    #     return self.content_object

    def deploy(self):
        for snt in self.servicenodetype_set.all():
            snt.deploy()

    def get_service_config(self):
        project_id = self.gitlab_project_id
        config = GitlabProject.get_config(project_id)
        return json.loads(config['config_content'])

    # @classmethod
    # def get_service_by_name_version(cls, name, version):
    #     service = cls.objects.get(service_config__contains={"service_name": name},
    #                               servicenodetype__version=int(version))
    #     return service


class ServiceNodeType(BaseModel):
    service = models.ForeignKey('services.Service')
    version = models.IntegerField(default=1)
    server_type = models.CharField(choices=SERVER_TYPES, max_length=4, default='STAG')
    api_gateway = models.ForeignKey('servers.APIGateway', null=True, blank=True)

    class Meta:
        unique_together = ('service', 'server_type', 'version')

    def __unicode__(self):
        return '{} | {} v{}'.format(self.server_type, self.service.service_name, self.version)

    def deploy(self):
        for ins in self.serviceinstance_set.all():
            ins.deploy()


class ServiceInstance(BaseNode):
    instance = models.IntegerField(default=1)
    service_node_type = models.ForeignKey('services.ServiceNodeType')

    class Meta:
        unique_together = ('server', 'service_node_type', 'is_active')

    def __unicode__(self):
        return '{} | {}'.format(self.service_node_type, self.server)

    def save(self, *args, **kwargs):
        super(ServiceInstance, self).save(*args, **kwargs)
        if self.is_created:
            service_node = ServiceNode()
            service_node.instance = self
            same_server_nodes = ServiceNode.objects.filter(instance__server=self.server).order_by('-http_port')
            if same_server_nodes.exists():
                node = same_server_nodes.first()
                service_node.http_port = node.http_port + 2
                service_node.tcp_port = service_node.http_port + 1
            service_node.save()

    def deploy(self):
        for node in self.servicenode_set.all():
            node.deploy()


class ServiceNode(BaseModel):
    instance = models.ForeignKey('services.ServiceInstance')

    http_host = models.CharField(max_length=100, default='0.0.0.0')
    http_port = models.IntegerField(default=DEFAULT_HTTP_PORT)

    tcp_host = models.CharField(max_length=100, default='0.0.0.0')
    tcp_port = models.IntegerField(default=DEFAULT_TCP_PORT)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='Database Type', null=True,
                                     blank=True)

    service_registry = models.ForeignKey('services.ServiceRegistryNode')
    database_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'database_id')
    dependencies = JSONField(null=True, blank=True)

    service_config = JSONField(null=True, blank=True)
    optional_settings = JSONField(null=True, blank=True)

    # class Meta:
    #     unique_together = ('instance', 'is_active')

    def __unicode__(self):
        return '{}'.format(self.instance)

    def save(self, *args, **kwargs):
        # self.service_config = self.service.get_service_config()
        super(ServiceNode, self).save(*args, **kwargs)
        options = dict()
        if self.is_created:
            options['database'] = True
            options['tags'] = ['prepare', 'trellio', 'service']
        else:
            options['tags'] = ['deploy']
        deploy_service.delay(self.pk, **options)

    def deploy(self):
        deploy_service.delay(self.pk, tags=['deploy'])

    @property
    def service(self):
        return self.instance.service_node_type.service

    @property
    def service_verbose_name(self):
        return '{}'.format(self.service.service_name)

    @property
    def pip_repo_url(self):
        repo_url = self.service.repo_url
        if self.instance.service_node_type.server_type == 'STAG':
            repo_url += '@staging'
        if 'http' in repo_url:
            return repo_url
        return 'ssh://{}'.format(repo_url.replace(':', '/'))

    @property
    def git_repo_url(self):
        return self.instance.service_node_type.service.repo_url

    @property
    def gitlab_project_id(self):
        return self.instance.service_node_type.service.gitlab_project_id

    @property
    def ip_address(self):
        return self.instance.server.ip_address

    @property
    def service_version(self):
        return self.instance.service_node_type.version

    @property
    def service_name(self):
        config = self.service_config
        if not config.get('SERVICE_NAME'):
            raise Exception('service_name not found service_config')
        return config['SERVICE_NAME']

    @property
    def service_uri(self):
        return self.instance.service_node_type.service.service_uri

    def get_config_file(self):
        project_id = self.service.gitlab_project_id
        return GitlabProject.get_config(project_id)

    def get_database(self):
        return self.content_object

    def get_config(self):
        optional_settings = dict()
        config = dict()
        config['HOST_NAME'] = self.instance.server.host_name
        config['SERVICE_VERSION'] = self.service_version
        config['HTTP_HOST'] = self.http_host
        config['HTTP_PORT'] = self.http_port
        config['TCP_HOST'] = self.tcp_host
        config['TCP_PORT'] = self.tcp_port
        config['REGISTRY_HOST'] = self.service_registry.registry_host
        config['REGISTRY_PORT'] = self.service_registry.registry_port
        config['REDIS_HOST'] = self.service_registry.redis.database_host
        config['REDIS_PORT'] = self.service_registry.redis.database_port

        database = self.get_database()
        if database:
            config['DATABASE_SETTINGS'] = database.get_database_settings()

        if self.service.smtp_server:
            config['SMTP_SETTINGS'] = self.service.smtp_server.get_smtp_settings()

        if self.service.contributors:
            config['ADMIN_EMAILS'] = self.service.contributors

        if self.optional_settings and isinstance(self.optional_settings, dict):
            config.update(self.optional_settings)

        return config


class ServiceRegistryNode(BaseNode):
    registry_host = models.CharField(max_length=100)
    registry_port = models.IntegerField(default=4500)
    redis = models.ForeignKey('databases.RedisNode')

    class Meta:
        unique_together = ('server', 'registry_port', 'is_active')

    def __unicode__(self):
        return '{}:{}'.format(self.registry_host, self.registry_port)

    def save(self, *args, **kwargs):
        if not self.registry_host:
            self.registry_host = self.server.ip_address
        super(ServiceRegistryNode, self).save(*args, **kwargs)


class TrellioAdmin(BaseNode):
    project_name = models.CharField(max_length=100, unique=True)
    project_owner = models.EmailField(max_length=200)
    repo_url = models.CharField(max_length=200, unique=True)
    domain = models.CharField(max_length=200, unique=True)

    def save(self, *args, **kwargs):
        super(TrellioAdmin, self).save(*args, **kwargs)
        from .tasks import deploy_trellio_admin
        tags = []
        if self.is_created:
            tags = ['prepare', 'setup']
        deploy_trellio_admin.delay(self.pk, extra_tags=tags)

    def get_environment_variables(self):
        env_vars = dict()
        env_vars['DEPLOYMENT_TYPE'] = 'PRODUCTION'

        return env_vars

    def get_db_user(self):
        return 'trellioadmin'

    def get_db_pass(self):
        return 'trellioadmin'

    def get_db_name(self):
        return 'trellioadmin'

    def deploy(self):
        from .tasks import deploy_trellio_admin
        deploy_trellio_admin.delay(self.pk)


from .tasks import *


@receiver(post_save, sender=ServiceRegistryNode)
def initiate_registry_node_tasks(sender, instance, **kwargs):
    deploy_registry.delay(instance.pk, extra_tags=['prepare'])

# @receiver(post_save, sender=ServiceNode)
# def initiate_service_node_tasks(sender, instance, **kwargs):
#     deploy_service.delay(instance.pk)
