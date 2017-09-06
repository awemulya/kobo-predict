# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('eventlog', '0014_auto_20170901_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightlog',
            name='extra_content_type',
            field=models.ForeignKey(related_name='notify_object', blank=True, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='fieldsightlog',
            name='extra_object_id',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
