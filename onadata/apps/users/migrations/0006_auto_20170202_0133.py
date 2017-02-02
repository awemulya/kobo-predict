# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import onadata.apps.users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_userprofile_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(default=b'logo/default_user.png', upload_to=onadata.apps.users.models.user_directory_path),
        ),
    ]
