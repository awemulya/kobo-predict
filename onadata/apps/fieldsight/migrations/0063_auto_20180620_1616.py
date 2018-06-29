# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0062_auto_20180613_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='site_meta_attributes_ans',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]
