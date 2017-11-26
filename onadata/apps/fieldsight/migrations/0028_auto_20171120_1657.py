# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0027_auto_20171120_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='timezone',
            name='country',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='timezone',
            name='country_code',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='timezone',
            name='city',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
