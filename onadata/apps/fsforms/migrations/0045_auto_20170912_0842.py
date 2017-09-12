# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0044_auto_20170807_1337'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationmaterial',
            name='fsxf',
            field=models.OneToOneField(related_name='em', null=True, blank=True, to='fsforms.FieldSightXF'),
        ),
        migrations.AlterField(
            model_name='educationmaterial',
            name='stage',
            field=models.OneToOneField(related_name='em', null=True, blank=True, to='fsforms.Stage'),
        ),
    ]
