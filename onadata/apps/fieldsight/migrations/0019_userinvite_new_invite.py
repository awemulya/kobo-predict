# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0018_auto_20170818_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinvite',
            name='new_invite',
            field=models.BooleanField(default=False),
        ),
    ]
