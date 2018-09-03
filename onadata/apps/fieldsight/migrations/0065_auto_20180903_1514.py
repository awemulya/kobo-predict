# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0064_site_current_progress'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectGeoJSON',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('geoJSON', models.FileField(max_length=755, null=True, upload_to=b'', blank=True)),
                ('project', models.OneToOneField(related_name='project_geojson', to='fieldsight.Project')),
            ],
        ),
        migrations.AddField(
            model_name='site',
            name='current_status',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='site',
            name='current_progress',
            field=models.IntegerField(default=0),
        ),
    ]
