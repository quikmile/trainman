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
admin.site.register(TrellioAdmin)
# import os
#
# from django.apps import apps
#
# from ..custom.utils import register_all_models
#
# app_label = os.path.abspath(__file__).split('/')[-2]
# app = apps.get_app_config(app_label)
# register_all_models(models=app.models, database=app_label)
