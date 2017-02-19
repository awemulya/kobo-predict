# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0028_auto_20170210_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightxf',
            name='fsform',
            field=models.ForeignKey(related_name='parent', blank=True, to='fsforms.FieldSightXF', null=True),
        ),
    ]
