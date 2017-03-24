# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0037_auto_20170321_2149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finstance',
            name='project',
            field=models.ForeignKey(related_name='project_instances', to='fieldsight.Project', null=True),
        ),
    ]
