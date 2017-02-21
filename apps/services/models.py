# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields.array import ArrayField
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models

from ..base.models import BaseModel, BaseNode

SERVER_TYPES = (('STAG', 'Staging'),
                ('PROD', 'Production'))

DATABASE_SERVER = (('On Service Host', 'On Service Host'),
                   ('Remote Host', 'Remote Host'))

HTTP_SERVER = (('NGINX', 'NGINX'),)


class Service(BaseModel):
    service_name = models.CharField(max_length=100, unique=True)
    repo_url = models.URLField(unique=True)
    contributors = ArrayField(models.CharField(max_length=300), null=True, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='Database Type', null=True,
                                     blank=True)

    database_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'database_id')
    dependencies = JSONField(null=True, blank=True)

    http_server = models.CharField(choices=HTTP_SERVER, max_length=20, default='NGINX')

    def __unicode__(self):
        return '{}'.format(self.service_name)


class ServiceNodeType(BaseModel):
    service = models.ForeignKey('services.Service')
    version = models.IntegerField(default=1)
    server_type = models.CharField(choices=SERVER_TYPES, max_length=4, default='STAG')
    instances = models.IntegerField(default=1)

    class Meta:
        unique_together = ('service', 'server_type', 'version')

    def __unicode__(self):
        return '{} | {} v{}'.format(self.server_type, self.service.service_name, self.version)

    def save(self, *args, **kwargs):
        super(ServiceNodeType, self).save(*args, **kwargs)


class ServiceNode(BaseNode):
    service = models.ForeignKey('services.Service')
    service_node_type = models.ForeignKey('services.ServiceNodeType')
    instance = models.IntegerField(default=1)

    http_host = models.CharField(max_length=100)
    http_port = models.IntegerField(default=8000)

    tcp_host = models.CharField(max_length=100)
    tcp_port = models.IntegerField(default=8001)

    registry = models.ForeignKey('services.ServiceRegistryNode')

    signals = JSONField(null=True, blank=True)
    optional_settings = JSONField(null=True, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='Database Node', null=True,
                                     blank=True)
    database_node_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'database_node_id')

    class Meta:
        unique_together = ('server', 'service', 'service_node_type', 'instance', 'service_version', 'is_active')

    def __unicode__(self):
        return '{} {}'.format(self.server.host_name, self.service.service_name)


class ServiceRegistryNode(BaseNode):
    registry_host = models.CharField(max_length=100)
    registry_port = models.IntegerField(default=4500)
    redis = models.ForeignKey('databases.RedisNode')

    class Meta:
        unique_together = ('server', 'registry_port', 'is_active')

    def __unicode__(self):
        return '{}:{}'.format(self.registry_host, self.registry_port)
