# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0007_auto_20161214_0334'),
        ('fsforms', '0020_auto_20170103_0413'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='project',
            field=models.ForeignKey(related_name='schedules', blank=True, to='fieldsight.Project', null=True),
        ),
        migrations.AddField(
            model_name='stage',
            name='project',
            field=models.ForeignKey(related_name='stages', blank=True, to='fieldsight.Project', null=True),
        ),
    ]
