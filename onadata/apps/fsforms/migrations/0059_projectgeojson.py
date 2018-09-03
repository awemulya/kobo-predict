# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0065_auto_20180903_1514'),
        ('fsforms', '0058_finstance_is_deleted'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectGeoJSON',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('jsonfile', models.FileField(upload_to=b'')),
                ('project', models.ForeignKey(related_name='geojson', to='fieldsight.Project')),
            ],
        ),
    ]
