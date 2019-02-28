# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0067_auto_20190225_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Type of Organization', blank=True, to='fieldsight.OrganizationType', null=True),
        ),
    ]
