# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0015_chatmessage'),
        ('eventlog', '0007_auto_20170531_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightlog',
            name='organization',
            field=models.ForeignKey(related_name='logs', default=1, to='fieldsight.Organization'),
            preserve_default=False,
        ),
    ]
