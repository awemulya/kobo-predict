# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0036_auto_20170321_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldsightxf',
            name='schedule',
            field=models.OneToOneField(related_name='schedule_forms', null=True, blank=True, to='fsforms.Schedule'),
        ),
        migrations.AlterField(
            model_name='fieldsightxf',
            name='stage',
            field=models.OneToOneField(related_name='stage_forms', null=True, blank=True, to='fsforms.Stage'),
        ),
    ]
