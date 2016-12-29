# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0018_schedule_site'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stage',
            name='site',
            field=models.ForeignKey(related_name='stages', blank=True, to='fieldsight.Site', null=True),
        ),
    ]
