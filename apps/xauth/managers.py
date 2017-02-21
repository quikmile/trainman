from datetime import datetime

from django.contrib.auth.base_user import BaseUserManager
from django.db.models.query import QuerySet


class XUserQueryset(QuerySet):
    def update(self, *args, **kwargs):
        for i in self.all():
            i.updated_on = datetime.now()
        super(XUserQueryset, self).update(**kwargs)

    def active(self):
        return self.filter(is_active=True)


class XUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        """
        Creates and saves a User with the given email, role and password.
        """
        if not username:
            raise ValueError('Users must have an username address')

        user = self.model(
            username=self.normalize_email(username)
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        """
        Creates and saves a superuser with the given email, role and password.
        """
        user = self.create_user(username,
                                password=password
                                )
        user.is_admin = True
        user.save(using=self._db)
        return user

    def get_queryset(self, *args, **kwargs):
        return XUserQueryset(self.model).order_by('-created_on')
