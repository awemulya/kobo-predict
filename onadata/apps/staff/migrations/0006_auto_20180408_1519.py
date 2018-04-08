# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0005_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='team',
            field=models.ForeignKey(related_name='attandence_team', blank=True, to='staff.Team', null=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='updated_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='staff',
            name='updated_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='updated_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
