# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0012_auto_20170216_1141'),
        ('fsforms', '0031_auto_20170220_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='formgroup',
            name='is_global',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='formgroup',
            name='organization',
            field=models.ForeignKey(blank=True, to='fieldsight.Organization', null=True),
        ),
        migrations.AddField(
            model_name='formgroup',
            name='project',
            field=models.ForeignKey(blank=True, to='fieldsight.Project', null=True),
        ),
        migrations.AlterField(
            model_name='formgroup',
            name='name',
            field=models.CharField(unique=True, max_length=256),
        ),
    ]
