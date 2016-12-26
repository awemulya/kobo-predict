# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0007_auto_20161214_0334'),
        ('fsforms', '0015_fieldsightxf_form_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='stage',
            name='site',
            field=models.ForeignKey(blank=True, to='fieldsight.Site', null=True),
        ),
    ]
