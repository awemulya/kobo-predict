# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0010_auto_20180417_1625'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='designation',
            field=models.IntegerField(default=1, choices=[(1, b'TSC Agent'), (2, b'Social Mobilizer'), (3, b'Senior Builder-Trainer'), (4, b'Junior Builder-Trainer')]),
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together=set([('attendance_date', 'team', 'is_deleted')]),
        ),
    ]
