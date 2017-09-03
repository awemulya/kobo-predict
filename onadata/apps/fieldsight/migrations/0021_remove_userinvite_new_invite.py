# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0020_userinvite_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinvite',
            name='new_invite',
        ),
    ]
