# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0002_auto_20180402_1157'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='staffs',
        ),
        migrations.AddField(
            model_name='attendance',
            name='staffs',
            field=models.ManyToManyField(to='staff.Staff', null=True, blank=True),
        ),
    ]
