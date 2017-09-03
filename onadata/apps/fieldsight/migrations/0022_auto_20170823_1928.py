# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0021_remove_userinvite_new_invite'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userinvite',
            old_name='reg_status',
            new_name='is_declied',
        ),
        migrations.AddField(
            model_name='userinvite',
            name='is_used',
            field=models.BooleanField(default=False),
        ),
    ]
