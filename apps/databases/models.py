# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.postgres.fields.array import ArrayField
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models

from apps.custom.utils import get_random_string
from ..base.models import BaseDatabaseNode, BaseModel


class Postgres(BaseModel):
    DEPLOYMENT_SERVER = (
        ('On Service Host', 'On Service Host'),
        ('Remote Host', 'Remote Host')
    )

    server = models.ForeignKey('servers.Server')
    database_extensions = ArrayField(models.CharField(max_length=50), null=True, blank=True)

    # slaves = models.IntegerField(default=0)

    class Meta:
        unique_together = ('server', 'slaves', 'database_extension')

    def __unicode__(self):
        return '{} | Extensions - {}'.format(self.server.host_xname, ', '.join(self.database_extensions))


class PostgresNode(BaseDatabaseNode):
    postgres = models.ForeignKey('databases.Postgres')
    master = models.ForeignKey('self', null=True, blank=True)
    database_name = models.CharField(max_length=100, unique=True)
    database_host = models.CharField(max_length=100)
    database_port = models.IntegerField(default=5432)
    database_user = models.CharField(max_length=100)
    database_password = models.CharField(max_length=100)
    optional_settings = JSONField(null=True, blank=True)

    class Meta:
        unique_together = ('database_host', 'database_port')

    def save(self, *args, **kwargs):
        if not self.database_name:
            self.database_name = self.generate_database_name()
        if not self.database_user:
            self.database_user = self.generate_database_user()
        if not self.database_password:
            self.database_user = self.generate_database_password()

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


class RedisNode(BaseDatabaseNode):
    master = models.ForeignKey('self', null=True, blank=True)
    database_name = models.CharField(max_length=100, unique=True)
    database_host = models.CharField(max_length=100, default='0.0.0.0')
    database_port = models.IntegerField(default=6379)
    database_user = models.CharField(max_length=100, null=True, blank=True)
    database_password = models.CharField(max_length=100, null=True, blank=True)
    optional_settings = JSONField(null=True, blank=True)

    class Meta:
        unique_together = ('server', 'database_port')
