# -*- coding: utf-8 -*-
# Generated by Django 1.11a1 on 2017-02-17 11:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.IntegerField(blank=True, default=1487330922, null=True)),
                ('updated_on', models.IntegerField(blank=True, default=1487330922, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('host_name', models.CharField(max_length=100)),
                ('ip_address', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
