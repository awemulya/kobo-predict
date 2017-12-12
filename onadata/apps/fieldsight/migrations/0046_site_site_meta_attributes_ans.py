# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0045_project_site_meta_attributes'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='site_meta_attributes_ans',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
    ]
