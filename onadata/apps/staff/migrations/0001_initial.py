# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attendance_date', models.DateTimeField()),
                ('created_date', models.DateTimeField()),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('staffs', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('submitted_by', models.ForeignKey(related_name='attendance_submitted_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Staffs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('full_name', models.CharField(max_length=255, null=True, blank=True)),
                ('type', models.IntegerField(default=0, choices=[(1, b'Laborer'), (2, b'Worker'), (3, b'Transporter')])),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(related_name='staff_created_by', to=settings.AUTH_USER_MODEL)),
                ('team_leader', models.ForeignKey(related_name='staff_teamleader', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
