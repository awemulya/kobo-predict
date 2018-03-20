# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0025_remove_celerytaskprogress_date_updateded'),
    ]

    operations = [
        migrations.AddField(
            model_name='celerytaskprogress',
            name='date_updateded',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
