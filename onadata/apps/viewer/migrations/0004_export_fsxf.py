# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0046_fieldsightxf_is_survey'),
        ('viewer', '0003_auto_20160912_0311'),
    ]

    operations = [
        migrations.AddField(
            model_name='export',
            name='fsxf',
            field=models.ForeignKey(related_name='exports', blank=True, to='fsforms.FieldSightXF', null=True),
        ),
    ]
