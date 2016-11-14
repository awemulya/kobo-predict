# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0002_auto_20161108_0034'),
        ('logger', '0005_remove_xform_site'),
    ]

    operations = [
        migrations.CreateModel(
            name='FieldSightXF',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_staged', models.BooleanField(default=False)),
                ('is_scheduled', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('date_modified',),
                'db_table': 'fieldsight_forms_data',
                'verbose_name': 'XForm',
                'verbose_name_plural': 'XForms',
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name=b'Schedule Name')),
                ('date_range_start', models.DateField(auto_now=True)),
                ('date_range_end', models.DateField(auto_now=True)),
            ],
            options={
                'ordering': ('date_range_start',),
                'db_table': 'fieldsight_forms_schedule',
                'verbose_name': 'Form Schedule',
                'verbose_name_plural': 'Form Schedules',
            },
        ),
        migrations.CreateModel(
            name='Stage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('order', models.IntegerField(default=0)),
                ('stage', models.ForeignKey(related_name='parent', blank=True, to='fsforms.Stage', null=True)),
            ],
            options={
                'ordering': ('order',),
                'db_table': 'fieldsight_forms_stage',
                'verbose_name': 'FieldSight Form Stage',
                'verbose_name_plural': 'FieldSight Form Stages',
            },
        ),
        migrations.AddField(
            model_name='fieldsightxf',
            name='schedule',
            field=models.ForeignKey(blank=True, to='fsforms.Schedule', null=True),
        ),
        migrations.AddField(
            model_name='fieldsightxf',
            name='site',
            field=models.ManyToManyField(related_name='site_forms', to='fieldsight.Site'),
        ),
        migrations.AddField(
            model_name='fieldsightxf',
            name='stage',
            field=models.ForeignKey(blank=True, to='fsforms.Stage', null=True),
        ),
        migrations.AddField(
            model_name='fieldsightxf',
            name='xf',
            field=models.ForeignKey(to='logger.XForm'),
        ),
    ]
