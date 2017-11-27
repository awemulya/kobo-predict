# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0035_auto_20171126_1301'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Timezone',
        ),
    ]
