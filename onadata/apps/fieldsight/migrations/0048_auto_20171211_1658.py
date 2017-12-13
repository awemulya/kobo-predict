# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0047_auto_20171211_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='site_meta_attributes',
            field=jsonfield.fields.JSONField(default=list),
        ),
    ]
