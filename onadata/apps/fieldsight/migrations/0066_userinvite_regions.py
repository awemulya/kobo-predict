# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0065_auto_20180903_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinvite',
            name='regions',
            field=models.ManyToManyField(related_name='invite_region_roles', to='fieldsight.Region'),
        ),
    ]
