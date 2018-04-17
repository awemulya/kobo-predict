# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0057_auto_20180408_1416'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sitetype',
            unique_together=set([('identifier', 'project')]),
        ),
    ]
