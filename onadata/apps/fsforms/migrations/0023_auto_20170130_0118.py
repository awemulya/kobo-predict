# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0007_auto_20161214_0334'),
        ('fsforms', '0022_fieldsightparsedinstance'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightxf',
            name='project',
            field=models.ForeignKey(related_name='project_forms', blank=True, to='fieldsight.Project', null=True),
        ),
        migrations.AddField(
            model_name='stage',
            name='ready',
            field=models.BooleanField(default=False),
        ),
    ]
