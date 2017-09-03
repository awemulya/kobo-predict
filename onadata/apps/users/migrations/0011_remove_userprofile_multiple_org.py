# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_userprofile_multiple_org'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='multiple_org',
        ),
    ]
