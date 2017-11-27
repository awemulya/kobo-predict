# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0037_timezone'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Timezone',
        ),
    ]
