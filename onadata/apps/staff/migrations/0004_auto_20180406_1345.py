# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('staff', '0003_auto_20180404_1239'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(related_name='team_created_by', to=settings.AUTH_USER_MODEL)),
                ('leader', models.ForeignKey(related_name='team_leader', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='staff',
            name='team_leader',
        ),
        migrations.AddField(
            model_name='staff',
            name='team',
            field=models.ForeignKey(related_name='staff_team', blank=True, to='staff.Team', null=True),
        ),
    ]
