# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0014_remove_fieldsightxf_form_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightxf',
            name='form_status',
            field=models.IntegerField(default=0, choices=[(0, b'Outstanding'), (1, b'Flagged'), (2, b'Approved'), (3, b'Rejected')]),
        ),
    ]
