# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('eventlog', '0003_auto_20170522_1154'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fieldsightlog',
            name='form',
        ),
        migrations.RemoveField(
            model_name='fieldsightlog',
            name='instance',
        ),
        migrations.RemoveField(
            model_name='fieldsightlog',
            name='profile',
        ),
        migrations.RemoveField(
            model_name='fieldsightlog',
            name='site',
        ),
        migrations.AddField(
            model_name='fieldsightlog',
            name='content_type',
            field=models.ForeignKey(default=1, to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fieldsightlog',
            name='object_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
