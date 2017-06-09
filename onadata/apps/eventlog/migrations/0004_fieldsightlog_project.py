# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0015_chatmessage'),
        ('eventlog', '0003_auto_20170522_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightlog',
            name='project',
            field=models.ForeignKey(related_name='log', to='fieldsight.Project', null=True),
        ),
    ]
