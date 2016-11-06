# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import django.contrib.gis.db.models.fields
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtraUserDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', jsonfield.fields.JSONField(default={})),
                ('user', models.OneToOneField(related_name='extra_details', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('address', models.TextField(null=True, blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, geography=True, blank=True)),
                ('phone', models.CharField(max_length=255, null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('fax', models.CharField(max_length=255, null=True, blank=True)),
                ('website', models.URLField(null=True, blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('address', models.TextField(null=True, blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, geography=True, blank=True)),
                ('phone', models.CharField(max_length=255, null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('fax', models.CharField(max_length=255, null=True, blank=True)),
                ('website', models.URLField(null=True, blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('organization', models.ForeignKey(related_name='projects', to='fieldsight.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('address', models.TextField(null=True, blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, geography=True, blank=True)),
                ('phone', models.CharField(max_length=255, null=True, blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('project', models.ForeignKey(related_name='sites', to='fieldsight.Project')),
            ],
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('started_at', models.DateTimeField(default=datetime.datetime.now)),
                ('ended_at', models.DateTimeField(null=True, blank=True)),
                ('group', models.ForeignKey(to='auth.Group')),
                ('organization', models.ForeignKey(related_name='organization_roles', blank=True, to='fieldsight.Organization', null=True)),
                ('project', models.ForeignKey(related_name='project_roles', blank=True, to='fieldsight.Project', null=True)),
                ('site', models.ForeignKey(related_name='site_roles', blank=True, to='fieldsight.Site', null=True)),
                ('user', models.ForeignKey(related_name='user_roles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='userrole',
            unique_together=set([('user', 'group', 'organization', 'project', 'site')]),
        ),
    ]
