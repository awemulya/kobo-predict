# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logger', '0002_xform_site_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='xform',
            name='site_users',
        ),
    ]
