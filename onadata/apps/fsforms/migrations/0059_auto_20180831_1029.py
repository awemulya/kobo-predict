# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0058_finstance_is_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finstance',
            name='site_fxf',
            field=models.ForeignKey(related_name='site_form_instances', on_delete=django.db.models.deletion.SET_NULL, to='fsforms.FieldSightXF', null=True),
        ),
    ]
