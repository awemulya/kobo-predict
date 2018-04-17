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
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('full_name', models.CharField(max_length=255, null=True, blank=True)),
                ('type', models.IntegerField(default=0, choices=[(1, b'Laborer'), (2, b'Worker'), (3, b'Transporter')])),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(related_name='staff_created_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(related_name='team_created_by', to=settings.AUTH_USER_MODEL)),
                ('leader', models.ForeignKey(related_name='team_leader', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='staff',
            name='team',
            field=models.ForeignKey(related_name='staff_team', blank=True, to='staff.Team', null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='staffs',
            field=models.ManyToManyField(to='staff.Staff', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='submitted_by',
            field=models.ForeignKey(related_name='attendance_submitted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attendance',
            name='team',
            field=models.ForeignKey(related_name='attandence_team', blank=True, to='staff.Team', null=True),
        ),
    ]
