# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0011_auto_20180425_0850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='staffs',
            field=models.ManyToManyField(to='staff.Staff'),
        ),
    ]
