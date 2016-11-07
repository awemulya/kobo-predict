# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import onadata.apps.users.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(max_length=140)),
                ('gender', models.CharField(max_length=140)),
                ('phone', models.CharField(max_length=140)),
                ('skype', models.CharField(max_length=140)),
                ('profile_picture', models.ImageField(upload_to=onadata.apps.users.models.user_directory_path, blank=True)),
                ('user', models.OneToOneField(related_name='user_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
