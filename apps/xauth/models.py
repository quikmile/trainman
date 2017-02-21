from __future__ import unicode_literals

import binascii
import os
import time

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from .managers import *


class XUser(AbstractBaseUser):
    username = models.EmailField(verbose_name='Email', max_length=255, unique=True)
    token = models.CharField(max_length=40, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_on = models.IntegerField(null=True, blank=True, default=int(time.time()))
    updated_on = models.IntegerField(null=True, blank=True, default=int(time.time()))
    role = models.CharField(max_length=30, null=True, blank=True)

    objects = XUserManager()

    USERNAME_FIELD = 'username'

    def save(self, *args, **kwargs):
        if not self.role:
            if self.is_admin:
                self.role = 'admin'
        if not self.token:
            self.token = self.generate_token()
        if not self.pk:
            self.created_on = int(time.time())
        self.updated_on = int(time.time())
        return super(XUser, self).save(*args, **kwargs)

    @property
    def created(self):
        return datetime.fromtimestamp(self.created_on).strftime(settings.XDATE_FORMAT)

    @property
    def updated(self):
        return datetime.fromtimestamp(self.updated_on).strftime(settings.XDATE_FORMAT)

    def generate_token(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def get_full_name(self):
        # The user is identified by their email address
        return self.username

    def get_short_name(self):
        # The user is identified by their email address
        return self.username

    def __str__(self):  # __unicode__ on Python 2
        return self.username

    def __unicode__(self):  # __unicode__ on Python 2
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    @property
    def profile(self):
        try:
            return self.user
        except AttributeError:
            pass

        try:
            return self.client
        except AttributeError:
            pass

        return False

    @property
    def profile(self):
        try:
            return getattr(self, str(self.role), None)
        except:
            return None

    @property
    def name(self):
        try:
            return self.profile.name
        except:
            return self.username
