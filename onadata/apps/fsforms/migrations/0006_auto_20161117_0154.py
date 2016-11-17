# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0005_auto_20161116_0513'),
    ]

    operations = [
        migrations.CreateModel(
            name='Days',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.CharField(max_length=8)),
                ('index', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='schedule',
            name='selected_days',
            field=models.ManyToManyField(to='fsforms.Days'),
        ),
    ]
