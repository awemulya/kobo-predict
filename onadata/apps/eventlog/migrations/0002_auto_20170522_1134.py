# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0015_chatmessage'),
        ('eventlog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightlog',
            name='is_seen',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fieldsightlog',
            name='site',
            field=models.ForeignKey(related_name='log', to='fieldsight.Site', null=True),
        ),
    ]
