# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0044_region_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='site_meta_attributes',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
    ]
