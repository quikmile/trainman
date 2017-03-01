import time
from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet

from ..custom.middleware.global_request import get_current_request


class BaseQuery(QuerySet):
    def update(self, *args, **kwargs):
        for i in self.all():
            i.updated_on = int(time.time())
        super(BaseQuery, self).update(**kwargs)


class ActiveManager(models.Manager):
    def get_queryset(self):
        return BaseQuery(self.model).filter(is_active=True).order_by('-created_on')


class BaseManager(models.Manager):
    def get_queryset(self):
        return BaseQuery(self.model).order_by('-created_on')


class BaseModel(models.Model):
    created_on = models.IntegerField(null=True, blank=True, default=int(time.time()))
    updated_on = models.IntegerField(null=True, blank=True, default=int(time.time()))
    is_active = models.BooleanField(default=True)

    objects = BaseManager()
    active = ActiveManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.is_created = False
        if not self.pk:
            self.created_on = int(time.time())
            self.is_created = True
        self.updated_on = int(time.time())
        super(BaseModel, self).save(*args, **kwargs)

    @property
    def created(self):
        return datetime.fromtimestamp(self.created_on).strftime(settings.XDATE_FORMAT)

    @property
    def updated(self):
        return datetime.fromtimestamp(self.updated_on).strftime(settings.XDATE_FORMAT)

    @property
    def _created_(self):
        return datetime.fromtimestamp(self.created_on)

    @property
    def _updated_(self):
        return datetime.fromtimestamp(self.updated_on)


class XBaseModel(BaseModel):
    updated_by = models.ForeignKey('xauth.XUser', null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.updated_by:
            request = get_current_request()
            if request:
                self.updated_by = request.user
            else:
                if 'user_id' in kwargs:
                    self.updated_by = kwargs['user_id']

        super(XBaseModel, self).save(*args, **kwargs)

    @classmethod
    def generate_id(cls):
        count = str(cls.objects.all().count() + 1)
        id = '0' * (10 - len(count)) + count
        return id


class BaseNode(BaseModel):
    server = models.ForeignKey('servers.Server')

    class Meta:
        abstract = True

    def deploy(self):
        raise NotImplementedError


class BaseDatabaseNode(BaseNode):
    class Meta:
        abstract = True
