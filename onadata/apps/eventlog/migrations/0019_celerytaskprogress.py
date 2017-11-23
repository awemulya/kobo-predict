# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eventlog', '0018_auto_20171114_2108'),
    ]

    operations = [
        migrations.CreateModel(
            name='CeleryTaskProgress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_id', models.CharField(max_length=255)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_completed', models.DateTimeField(null=True, blank=True)),
                ('status', models.IntegerField(default=0, choices=[(0, 'Pending'), (1, 'In Progress'), (2, 'Completed')])),
                ('user', models.ForeignKey(related_name='task_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
