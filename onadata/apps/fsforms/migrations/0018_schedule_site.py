# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0007_auto_20161214_0334'),
        ('fsforms', '0017_auto_20161227_0209'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='site',
            field=models.ForeignKey(related_name='schedules', blank=True, to='fieldsight.Site', null=True),
        ),
    ]
