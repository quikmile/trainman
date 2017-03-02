# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from ..base.models import BaseModel

HTTP_SERVER = (('NGINX', 'NGINX'),)


class Server(BaseModel):
    host_name = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=100)

    def __unicode__(self):
        return '{} | {}'.format(self.host_name, self.ip_address)


class APIGateway(BaseModel):
    server = models.ForeignKey('servers.Server')
    http_server = models.CharField(choices=HTTP_SERVER, max_length=20, default='NGINX')

    def __unicode__(self):
        return '{} | {}'.format(self.server, self.http_server)

    def save(self, *args, **kwargs):
        super(APIGateway, self).save(*args, **kwargs)
        from .tasks import deploy_gateway
        deploy_gateway.delay()
