# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import onadata.apps.fieldsight.models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0054_region_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blueprints',
            name='image',
            field=models.FileField(upload_to=onadata.apps.fieldsight.models.get_image_filename, verbose_name='BluePrints'),
        ),
    ]
