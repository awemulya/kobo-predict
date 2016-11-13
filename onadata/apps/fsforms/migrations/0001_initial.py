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
                ('scheduled', models.BooleanField(default=True)),
                ('start', models.DateField(null=True, blank=True)),
                ('end', models.DateField(null=True, blank=True)),
                ('site', models.ManyToManyField(related_name='site_forms', to='fieldsight.Site', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Stages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('order', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SubStage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('stage', models.ForeignKey(related_name='sub_stage', to='fsforms.Stages')),
            ],
        ),
        migrations.AddField(
            model_name='fieldsightxf',
            name='sub_stage',
            field=models.ForeignKey(related_name='sub_stage', blank=True, to='fsforms.SubStage', null=True),
        ),
        migrations.AddField(
            model_name='fieldsightxf',
            name='xf',
            field=models.ForeignKey(to='logger.XForm'),
        ),
    ]
