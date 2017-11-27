# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('eventlog', '0019_celerytaskprogress'),
    ]

    operations = [
        migrations.AddField(
            model_name='celerytaskprogress',
            name='content_type',
            field=models.ForeignKey(related_name='task_object', blank=True, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='celerytaskprogress',
            name='description',
            field=models.CharField(max_length=755, blank=True),
        ),
        migrations.AddField(
            model_name='celerytaskprogress',
            name='object_id',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='celerytaskprogress',
            name='task_type',
            field=models.IntegerField(default=0, choices=[(0, 'Bulk Site Upload'), (1, 'Multi User Assign Project'), (2, 'Multi User Assign Site')]),
        ),
        migrations.AlterField(
            model_name='celerytaskprogress',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, 'Pending'), (1, 'In Progress'), (2, 'Completed'), (3, 'Failed')]),
        ),
        migrations.AlterField(
            model_name='celerytaskprogress',
            name='task_id',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
