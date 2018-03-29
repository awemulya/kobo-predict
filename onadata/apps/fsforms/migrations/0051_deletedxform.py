# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logger', '0005_remove_xform_site'),
        ('fsforms', '0050_stage_weight'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedXForm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('xf', models.OneToOneField(related_name='deleted_xform', to='logger.XForm')),
            ],
        ),
    ]
