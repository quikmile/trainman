# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.postgres.fields.array import ArrayField
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models

from ..base.models import BaseDatabaseNode, BaseModel


class Postgres(BaseModel):
    DEPLOYMENT_SERVER = (
        ('On Service Host', 'On Service Host'),
        ('Remote Host', 'Remote Host')
    )

    deployment_server = models.CharField(choices=DEPLOYMENT_SERVER, max_length=20, default='On Service Host')
    slaves = models.IntegerField(default=0)
    database_extension = ArrayField(models.CharField(max_length=50), null=True, blank=True)

    class Meta:
        unique_together = ('deployment_server', 'slaves', 'database_extension')


class PostgresNode(BaseDatabaseNode):
    master = models.ForeignKey('self', null=True, blank=True)
    database_name = models.CharField(max_length=100, unique=True)
    database_host = models.CharField(max_length=100)
    database_port = models.IntegerField(default=5432)
    database_user = models.CharField(max_length=100)
    database_password = models.CharField(max_length=100)
    optional_settings = JSONField(null=True, blank=True)

    class Meta:
        unique_together = ('server', 'database_port')


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
