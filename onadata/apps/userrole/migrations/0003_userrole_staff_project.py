# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0008_auto_20180412_1515'),
        ('userrole', '0002_auto_20170927_1311'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrole',
            name='staff_project',
            field=models.ForeignKey(related_name='staff_project_roles', blank=True, to='staff.StaffProject', null=True),
        ),
    ]
