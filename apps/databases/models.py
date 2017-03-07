# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.postgres.fields.array import ArrayField
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from ..base.models import BaseDatabaseNode, BaseModel
from ..custom.gitlab.project_apis import GitlabProject
from ..custom.utils import get_random_string
from ..services.models import Service

DEPLOYMENT_SERVER = (
    ('On Service Host', 'On Service Host'),
    ('Remote Host', 'Remote Host')
)


class Postgres(BaseModel):
    server = models.ForeignKey('servers.Server')
    database_extensions = ArrayField(models.CharField(max_length=50), null=True, blank=True)

    # slaves = models.IntegerField(default=0)

    # class Meta:
    #     unique_together = ('server', 'database_extensions')

    def __unicode__(self):
        return '{} | Extensions - {}'.format(self.server.host_name, ', '.join(self.database_extensions))

    def save(self, *args, **kwargs):
        created = False
        if not self.pk:
            created = True
        super(Postgres, self).save(*args, **kwargs)
        if created:
            postgres_node = PostgresNode()
            postgres_node.postgres = self
            postgres_node.save()

    def get_database_settings(self):
        master_db = self.postgresnode_set.filter(master__isnull=True).first()
        settings = dict()
        settings['database_name'] = master_db.database_name
        settings['database_host'] = master_db.database_host
        settings['database_port'] = master_db.database_port
        settings['database_user'] = master_db.database_user
        settings['database_password'] = master_db.database_password

        try:
            print master_db.optional_settings
            settings.update(master_db.optional_settings)
        except:
            pass
        return settings

    def get_service(self):
        return Service.objects.get(database_id=self.pk)

    def get_sql(self):
        service = self.get_service()
        return GitlabProject.get_sql(service.gitlab_project_id)

    def deploy(self):
        for db_node in self.postgresnode_set.all():
            db_node.deploy()


class PostgresNode(BaseModel):
    postgres = models.ForeignKey('databases.Postgres')
    master = models.ForeignKey('self', null=True, blank=True)
    database_name = models.CharField(max_length=100, unique=True)
    database_host = models.CharField(max_length=100)
    database_port = models.IntegerField(default=5432)
    database_user = models.CharField(max_length=100)
    database_password = models.CharField(max_length=100)
    optional_settings = JSONField(null=True, blank=True)

    # class Meta:
    #     unique_together = ('database_host', 'database_port')

    def __unicode__(self):
        return '{}'.format(self.postgres)

    def save(self, *args, **kwargs):
        if not self.database_host:
            self.database_host = self.postgres.server.ip_address

        if not self.database_name:
            self.database_name = self.generate_database_name()

        if not self.database_user:
            self.database_user = self.generate_database_user()

        if not self.database_password:
            self.database_password = self.generate_database_password()

        super(PostgresNode, self).save(*args, **kwargs)

    @staticmethod
    def generate_database_name():
        while True:
            db_name = get_random_string(length=12)
            if not PostgresNode.objects.filter(database_name=db_name).exists():
                break

        return db_name

    @staticmethod
    def generate_database_user():
        return get_random_string(length=10)

    @staticmethod
    def generate_database_password():
        return get_random_string(length=15)

    def deploy(self):
        deploy_postgres.delay(self.pk)


class RedisNode(BaseDatabaseNode):
    master = models.ForeignKey('self', null=True, blank=True)
    database_name = models.CharField(max_length=100, unique=True)
    database_host = models.CharField(max_length=100)
    database_port = models.IntegerField(default=6379)
    database_user = models.CharField(max_length=100, null=True, blank=True)
    database_password = models.CharField(max_length=100, null=True, blank=True)
    optional_settings = JSONField(null=True, blank=True)

    class Meta:
        unique_together = ('server', 'database_port')

    def __unicode__(self):
        return '{}'.format(self.server)

    def save(self, *args, **kwargs):
        if not self.database_host:
            self.database_host = self.server.ip_address
        if not self.database_name:
            self.database_name = get_random_string(8)
        if not self.database_user:
            self.database_name = get_random_string(8)
        if not self.database_password:
            self.database_name = get_random_string(10)
        super(RedisNode, self).save(*args, **kwargs)

    def deploy(self):
        deploy_redis.delay(self.pk)


from .tasks import *


@receiver(post_save, sender=PostgresNode)
def initiate_postgres_nodes_tasks(sender, instance, **kwargs):
    deploy_postgres.delay(instance.pk)


@receiver(post_save, sender=RedisNode)
def initiate_redis_node_tasks(sender, instance, **kwargs):
    deploy_redis.delay(instance.pk, extra_tags=['prepare'])
