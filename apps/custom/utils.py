import random
import string
from collections import OrderedDict

from django.contrib import admin


def get_random_string(length):
    prefix = ''.join(random.choice(string.ascii_lowercase) for _ in range(1))
    suffix = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length - 1))
    return prefix + suffix


def remove_quotes(string):
    if string.startswith('"') and string.endswith('"'):
        string = string[1:-1]
    return string


class MultiDBModelAdmin(admin.ModelAdmin):
    # A handy constant for the name of the alternate database.
    using = None

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super(MultiDBModelAdmin, self).get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super(MultiDBModelAdmin, self).formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super(MultiDBModelAdmin, self).formfield_for_manytomany(db_field, request, using=self.using, **kwargs)


def create_model_admin(model, database=None):
    fields = model._meta.get_fields()

    # print [f.get_internal_type() for f in fields]
    field_list = []
    for f in fields:
        if f.name == 'id' or f.get_internal_type() == 'ForeignKey' or f.get_internal_type() == 'ManyToManyField':
            continue
        field_list.append(f.name)

    class ModelAdmin(MultiDBModelAdmin):
        using = database

        list_display = field_list
        search_fields = field_list
        # list_filter = ['code']

    return ModelAdmin


def register_all_models(models=(), database=None):
    if models:
        if isinstance(models, OrderedDict):
            models = dict(models)
            for model_name, model in models.items():
                try:
                    model_admin = create_model_admin(model, database=database)
                    admin.site.register(model, model_admin)
                except Exception as e:
                    print(e)
        if isinstance(models, list):
            for model in models:
                try:
                    model_admin = create_model_admin(model, database=database)
                    admin.site.register(model, model_admin)
                except Exception as e:
                    print(e)
