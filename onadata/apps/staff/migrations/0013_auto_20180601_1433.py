# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0012_auto_20180513_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='designation',
            field=models.IntegerField(default=1, choices=[(1, b'TSC Agent'), (2, b'Social Mobilizer'), (3, b'Senior Builder-Trainer'), (4, b'Junior Builder-Trainer'), (5, b'Team Leader'), (6, b'Support Staff')]),
        ),
    ]
