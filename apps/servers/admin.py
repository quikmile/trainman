# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import *

admin.site.register(Server)
admin.site.register(APIGateway)
admin.site.register(SMTPServer)
# Register your models here.
