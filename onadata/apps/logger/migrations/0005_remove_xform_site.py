# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logger', '0004_xform_site'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='xform',
            name='site',
        ),
    ]
