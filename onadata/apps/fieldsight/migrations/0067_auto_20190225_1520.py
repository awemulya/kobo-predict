# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0066_auto_20190211_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitetype',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='site',
            name='type',
            field=models.ForeignKey(related_name='sites', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Type of Site', blank=True, to='fieldsight.SiteType', null=True),
        ),
    ]
