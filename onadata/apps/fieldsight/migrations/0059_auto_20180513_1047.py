# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0058_auto_20180408_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinvite',
            name='project',
            field=models.ManyToManyField(related_name='invite_project_roles', to='fieldsight.Project'),
        ),
        migrations.AlterField(
            model_name='userinvite',
            name='site',
            field=models.ManyToManyField(related_name='invite_site_roles', to='fieldsight.Site'),
        ),
    ]
