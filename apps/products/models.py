# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from ..base.models import BaseModel


class Product(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
