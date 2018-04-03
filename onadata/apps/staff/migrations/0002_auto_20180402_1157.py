# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Staff',
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
        migrations.RemoveField(
            model_name='staffs',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='staffs',
            name='team_leader',
        ),
        migrations.DeleteModel(
            name='Staffs',
        ),
    ]
