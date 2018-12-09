# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0065_auto_20180903_1514'),
        ('fsforms', '0066_submissionofflinesite'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionofflinesite',
            name='temporary_site',
            field=models.ForeignKey(related_name='offline_submissions', default=0, to='fieldsight.Site'),
            preserve_default=False,
        ),
    ]
