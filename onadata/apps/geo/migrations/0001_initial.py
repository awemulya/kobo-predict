# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0052_auto_20180109_1839'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=255, blank=True)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(default=None, srid=4326, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='GeoLayer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.IntegerField(default=1)),
                ('title', models.CharField(max_length=255)),
                ('title_prop', models.CharField(max_length=255, blank=True)),
                ('code_prop', models.CharField(max_length=255, blank=True)),
                ('geo_shape_file', models.FileField(upload_to='geo_layers/')),
                ('stale_areas', models.BooleanField(default=True)),
                ('organization', models.ForeignKey(related_name='geo_layers', to='fieldsight.Organization')),
            ],
            options={
                'ordering': ['level'],
            },
        ),
        migrations.AddField(
            model_name='geoarea',
            name='geo_layer',
            field=models.ForeignKey(related_name='geo_areas', to='geo.GeoLayer'),
        ),
    ]
