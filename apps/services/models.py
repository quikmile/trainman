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

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='Database Type', null=True,
                                     blank=True)

    service_registry = models.ForeignKey('services.ServiceRegistryNode')

    database_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'database_id')
    dependencies = JSONField(null=True, blank=True)

    http_server = models.CharField(choices=HTTP_SERVER, max_length=20, default='NGINX')
    service_uri = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return '{}'.format(self.service_name)

    def get_database(self):
        return self.content_object


class ServiceNodeType(BaseModel):
    service = models.ForeignKey('services.Service')
    version = models.IntegerField(default=1)
    server_type = models.CharField(choices=SERVER_TYPES, max_length=4, default='STAG')

    class Meta:
        unique_together = ('service', 'server_type', 'version')

    def __unicode__(self):
        return '{} | {} v{}'.format(self.server_type, self.service.service_name, self.version)


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
                service_node.http_host = node.http_port + 2
                service_node.tcp_port = node.tcp_port + 2
            service_node.save()


class ServiceNode(BaseModel):
    instance = models.ForeignKey('services.ServiceInstance')

    http_host = models.CharField(max_length=100, default='0.0.0.0')
    http_port = models.IntegerField(default=DEFAULT_HTTP_PORT)

    tcp_host = models.CharField(max_length=100, default='0.0.0.0')
    tcp_port = models.IntegerField(default=DEFAULT_TCP_PORT)

    optional_settings = JSONField(null=True, blank=True)

    # class Meta:
    #     unique_together = ('instance', 'is_active')

    def __unicode__(self):
        return '{}'.format(self.instance)

    @property
    def service(self):
        return self.instance.service_node_type.service

    @property
    def service_verbose_name(self):
        return '{}'.format(self.service.service_name)

    @property
    def pip_repo_url(self):
        repo_url = self.service.repo_url
        if 'http' in repo_url:
            return repo_url
        return 'ssh://{}'.format(repo_url.replace(':', '/'))

    @property
    def git_repo_url(self):
        return self.service.repo_url

    @property
    def ip_address(self):
        return self.instance.server.ip_address

    @property
    def service_version(self):
        return self.instance.service_node_type.version

    @property
    def service_uri(self):
        return self.instance.service_node_type.service.service_uri

    def get_service_directory(self):
        project_id = self.service.gitlab_project_id
        return GitlabProject.get_dir_name(project_id)

    def get_database(self):
        return self.service.get_database()

    def get_config(self):
        optional_settings = dict()
        config = dict()
        config['host_name'] = self.instance.server.host_name
        config['service_version'] = self.service_version
        config['http_host'] = self.http_host
        config['http_port'] = self.http_port
        config['tcp_host'] = self.tcp_host
        config['tcp_port'] = self.tcp_port
        config['registry_host'] = self.service.service_registry.registry_host
        config['registry_port'] = self.service.service_registry.registry_port
        config['redis_host'] = self.service.service_registry.redis.database_host
        config['redis_port'] = self.service.service_registry.redis.database_port

        if self.optional_settings and isinstance(self.optional_settings, dict):
            optional_settings = self.optional_settings

        config['signals'] = optional_settings.get('signals', {})
        config['middlewares'] = optional_settings.get('middlewares', {})

        database = self.get_database()
        database_settings = database.get_database_settings()
        config.update(database_settings)

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


from .tasks import *


@receiver(post_save, sender=ServiceRegistryNode)
def initiate_registry_node_tasks(sender, instance, **kwargs):
    deploy_registry.delay(instance.pk, extra_tags=['prepare'])


@receiver(post_save, sender=ServiceNode)
def initiate_service_node_tasks(sender, instance, **kwargs):
    deploy_service.delay(instance.pk)
