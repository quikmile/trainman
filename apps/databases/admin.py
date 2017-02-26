# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import *

admin.site.register(Postgres)
admin.site.register(PostgresNode)
admin.site.register(RedisNode)
# Register your models here.
