# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0065_auto_20180903_1514'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='site',
            unique_together=set([('identifier', 'project', 'is_active')]),
        ),
    ]
