# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0013_fieldsightxf_form_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fieldsightxf',
            name='form_status',
        ),
    ]
