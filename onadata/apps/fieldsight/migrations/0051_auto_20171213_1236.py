# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0050_auto_20171213_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='region',
            name='name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='region',
            name='project',
            field=models.ForeignKey(related_name='project_region', to='fieldsight.Project'),
            preserve_default=False,
        ),
    ]
