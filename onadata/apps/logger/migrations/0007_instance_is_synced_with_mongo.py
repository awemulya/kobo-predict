# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import onadata.apps.logger.fields


class Migration(migrations.Migration):

    dependencies = [
        ('logger', '0006_instance_xml_hash'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='is_synced_with_mongo',
            field=onadata.apps.logger.fields.LazyDefaultBooleanField(default=False),
        ),
    ]
