# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0068_submissionofflinesite_fieldsight_form'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissionofflinesite',
            name='instance',
            field=models.OneToOneField(related_name='offline_submission', null=True, blank=True, to='fsforms.FInstance'),
        ),
    ]
