# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0063_auto_20180620_1616'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ConnectedDomain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ConnectedProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(default=None, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RemoteApp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('auth_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('projects', models.ManyToManyField(to='fieldsight.Project', through='remote_app.ConnectedProject', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='connectedproject',
            name='app',
            field=models.ForeignKey(to='remote_app.RemoteApp'),
        ),
        migrations.AddField(
            model_name='connectedproject',
            name='project',
            field=models.ForeignKey(to='fieldsight.Project'),
        ),
        migrations.AddField(
            model_name='connecteddomain',
            name='app',
            field=models.ForeignKey(to='remote_app.RemoteApp'),
        ),
    ]
