# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fsforms', '0003_auto_20161114_1014'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('description', models.TextField(null=True, blank=True)),
                ('shared_level', models.IntegerField(default=2, choices=[(0, b'Global'), (1, b'Organization'), (2, b'Project')])),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(related_name='form_group', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-date_modified',),
                'db_table': 'fieldsight_forms_group',
                'verbose_name': 'FieldSight Form Group',
                'verbose_name_plural': 'FieldSight Form Groups',
            },
        ),
        migrations.AddField(
            model_name='fieldsightxf',
            name='shared_level',
            field=models.IntegerField(default=2, choices=[(0, b'Global'), (1, b'Organization'), (2, b'Project')]),
        ),
        migrations.AddField(
            model_name='schedule',
            name='shared_level',
            field=models.IntegerField(default=2, choices=[(0, b'Global'), (1, b'Organization'), (2, b'Project')]),
        ),
        migrations.AddField(
            model_name='stage',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 15, 21, 16, 42, 8242), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stage',
            name='date_modified',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 15, 21, 17, 7, 231119), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stage',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='stage',
            name='shared_level',
            field=models.IntegerField(default=2, choices=[(0, b'Global'), (1, b'Organization'), (2, b'Project')]),
        ),
        migrations.AddField(
            model_name='schedule',
            name='group',
            field=models.ForeignKey(related_name='schedule', default=1, to='fsforms.FormGroup'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stage',
            name='group',
            field=models.ForeignKey(related_name='stage', default=1, to='fsforms.FormGroup'),
            preserve_default=False,
        ),
    ]
