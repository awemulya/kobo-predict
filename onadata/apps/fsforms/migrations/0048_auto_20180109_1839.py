# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0047_fieldsightxf_from_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightxf',
            name='default_submission_status',
            field=models.IntegerField(default=0, choices=[(0, 'Pending'), (1, 'Rejected'), (2, 'Flagged'), (3, 'Approved')]),
        ),
        migrations.AlterField(
            model_name='finstance',
            name='form_status',
            field=models.IntegerField(blank=True, null=True, choices=[(0, 'Pending'), (1, 'Rejected'), (2, 'Flagged'), (3, 'Approved')]),
        ),
    ]
