# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0067_submissionofflinesite_temporary_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionofflinesite',
            name='fieldsight_form',
            field=models.ForeignKey(related_name='offline_submissiob', blank=True, to='fsforms.FieldSightXF', null=True),
        ),
    ]
