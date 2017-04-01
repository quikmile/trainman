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
    domain = models.CharField(max_length=100, null=True, blank=True)
    server = models.ForeignKey('servers.Server')
    http_server = models.CharField(choices=HTTP_SERVER, max_length=20, default='NGINX')

    def __unicode__(self):
        return '{} | {} | {}'.format(self.server, self.domain, self.http_server)

    def save(self, *args, **kwargs):
        super(APIGateway, self).save(*args, **kwargs)
        from .tasks import deploy_gateway
        extra_tags = []
        if self.is_created:
            extra_tags = ['prepare', 'nginx']
        deploy_gateway.delay(self.pk, extra_tags=extra_tags)


class SMTPServer(BaseModel):
    smtp_host = models.CharField(max_length=100)
    smtp_port = models.IntegerField(default=587)
    smtp_user = models.EmailField(max_length=200)
    smtp_password = models.CharField(max_length=100)

    class Meta:
        unique_together = ('smtp_host', 'smtp_port', 'smtp_user')

    def __unicode__(self):
        return '{} - {}'.format(self.smtp_host, self.smtp_user)

    def get_smtp_settings(self):
        settings = dict()
        settings['smtp_host'] = self.smtp_host
        settings['smtp_port'] = self.smtp_port
        settings['smtp_user'] = self.smtp_user
        settings['smtp_password'] = self.smtp_password
        return settings
