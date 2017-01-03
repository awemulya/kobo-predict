# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0019_auto_20161229_0115'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fieldsightinstance',
            name='fsxform',
        ),
        migrations.RemoveField(
            model_name='fieldsightinstance',
            name='instance',
        ),
        migrations.DeleteModel(
            name='FieldsightInstance',
        ),
    ]
