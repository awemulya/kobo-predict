# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0039_timezone'),
        ('users', '0012_userprofile_notification_seen_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='timezone',
            field=models.ForeignKey(blank=True, to='fieldsight.TimeZone', null=True),
        ),
    ]
