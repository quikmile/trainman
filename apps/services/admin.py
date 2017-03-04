# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import *


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'service_uri', 'content_object', 'database_id', 'contributors', 'service_registry')
    list_filter = ['service_registry', 'is_active']


admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceNode)
admin.site.register(ServiceNodeType)
admin.site.register(ServiceRegistryNode)
admin.site.register(ServiceInstance)
