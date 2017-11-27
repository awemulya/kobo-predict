# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0038_delete_timezone'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeZone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_zone', models.CharField(max_length=255, null=True, blank=True)),
                ('country', models.CharField(max_length=255, null=True, blank=True)),
                ('country_code', models.CharField(max_length=255, null=True, blank=True)),
                ('offset_time', models.CharField(max_length=255, blank=True)),
            ],
        ),
    ]
