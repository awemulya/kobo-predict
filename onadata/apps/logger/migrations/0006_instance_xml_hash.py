# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logger', '0005_remove_xform_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='xml_hash',
            field=models.CharField(default=None, max_length=64, null=True, db_index=True),
        ),
    ]
