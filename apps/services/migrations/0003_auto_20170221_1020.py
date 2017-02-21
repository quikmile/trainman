# -*- coding: utf-8 -*-
# Generated by Django 1.11a1 on 2017-02-21 10:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('databases', '0003_auto_20170221_1020'),
        ('servers', '0005_auto_20170221_1020'),
        ('services', '0002_auto_20170219_0912'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceRegistryNode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.IntegerField(blank=True, default=1487672395, null=True)),
                ('updated_on', models.IntegerField(blank=True, default=1487672395, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('registry_host', models.CharField(max_length=100)),
                ('registry_port', models.IntegerField(default=4500)),
                ('redis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='databases.RedisNode')),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='servers.Server')),
            ],
        ),
        migrations.RemoveField(
            model_name='servicenode',
            name='redis_host',
        ),
        migrations.RemoveField(
            model_name='servicenode',
            name='redis_port',
        ),
        migrations.RemoveField(
            model_name='servicenode',
            name='registry_host',
        ),
        migrations.RemoveField(
            model_name='servicenode',
            name='registry_port',
        ),
        migrations.AddField(
            model_name='servicenodetype',
            name='version',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='service',
            name='created_on',
            field=models.IntegerField(blank=True, default=1487672395, null=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='updated_on',
            field=models.IntegerField(blank=True, default=1487672395, null=True),
        ),
        migrations.AlterField(
            model_name='servicenode',
            name='created_on',
            field=models.IntegerField(blank=True, default=1487672395, null=True),
        ),
        migrations.AlterField(
            model_name='servicenode',
            name='updated_on',
            field=models.IntegerField(blank=True, default=1487672395, null=True),
        ),
        migrations.AlterField(
            model_name='servicenodetype',
            name='created_on',
            field=models.IntegerField(blank=True, default=1487672395, null=True),
        ),
        migrations.AlterField(
            model_name='servicenodetype',
            name='updated_on',
            field=models.IntegerField(blank=True, default=1487672395, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='servicenodetype',
            unique_together=set([('service', 'server_type', 'version')]),
        ),
        migrations.AddField(
            model_name='servicenode',
            name='registry',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='services.ServiceRegistryNode'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='serviceregistrynode',
            unique_together=set([('server', 'registry_port', 'is_active')]),
        ),
    ]
