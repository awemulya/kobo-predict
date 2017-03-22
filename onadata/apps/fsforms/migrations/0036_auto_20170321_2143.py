# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0035_instancestatuschanged_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='finstance',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 21, 21, 43, 55, 312431), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='fieldsightxf',
            name='schedule',
            field=models.ForeignKey(related_name='schedule_forms', blank=True, to='fsforms.Schedule', null=True),
        ),
        migrations.AlterField(
            model_name='fieldsightxf',
            name='stage',
            field=models.ForeignKey(related_name='stage_forms', blank=True, to='fsforms.Stage', null=True),
        ),
    ]
