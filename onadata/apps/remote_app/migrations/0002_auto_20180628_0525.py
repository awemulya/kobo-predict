# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('remote_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='connecteddomain',
            old_name='url',
            new_name='domain',
        ),
    ]
