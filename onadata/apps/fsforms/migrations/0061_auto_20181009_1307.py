# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import onadata.apps.fsforms.models


class Migration(migrations.Migration):

    dependencies = [
        ('logger', '0006_instance_xml_hash'),
        ('fsforms', '0060_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='XformHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('xls', models.FileField(null=True, upload_to=onadata.apps.fsforms.models.upload_to)),
                ('json', models.TextField(default='')),
                ('description', models.TextField(default='', null=True)),
                ('xml', models.TextField()),
                ('id_string', models.CharField(max_length=255, editable=False)),
                ('title', models.CharField(max_length=255, editable=False)),
                ('uuid', models.CharField(default='', max_length=32)),
                ('xform', models.ForeignKey(related_name='fshistory', to='logger.XForm')),
            ],
        ),
        migrations.RemoveField(
            model_name='projectgeojson',
            name='project',
        ),
        migrations.DeleteModel(
            name='ProjectGeoJSON',
        ),
    ]
