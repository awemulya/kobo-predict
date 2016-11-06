# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0002_auto_20161104_0835'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name=b'Project Type')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='additional_desc',
            field=models.TextField(null=True, verbose_name=b'Additional Description', blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='donor',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='public_desc',
            field=models.TextField(null=True, verbose_name=b'Public Description', blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='type',
            field=models.ForeignKey(default=1, verbose_name=b'Type of Project', to='fieldsight.ProjectType'),
            preserve_default=False,
        ),
    ]
