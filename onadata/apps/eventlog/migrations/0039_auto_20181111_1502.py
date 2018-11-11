# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('eventlog', '0038_auto_20181111_1501'),
    ]

    operations = [
        migrations.AddField(
            model_name='celerytaskprogress',
            name='content_type',
            field=models.ForeignKey(related_name='task_object', blank=True, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='celerytaskprogress',
            name='object_id',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
