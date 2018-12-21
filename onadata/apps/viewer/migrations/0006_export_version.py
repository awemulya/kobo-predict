# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0005_export_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='export',
            name='version',
            field=models.CharField(default=b'0', max_length=255, null=True, blank=True),
        ),
    ]
