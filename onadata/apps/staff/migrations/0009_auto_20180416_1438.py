# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0008_auto_20180412_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='photo',
            field=models.ImageField(default=b'/static/images/default_user.png', upload_to=b'staffs'),
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together=set([('attendance_date', 'team')]),
        ),
    ]
