# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import image_cropping.fields
import onadata.apps.users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20170202_0512'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name=b'cropping',
            field=image_cropping.fields.ImageRatioField(b'image', '255x255', hide_image_field=False, size_warning=False, allow_fullsize=False, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='cropping'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='image',
            field=image_cropping.fields.ImageCropField(upload_to=onadata.apps.users.models.user_directory_path, blank=True),
        ),
    ]
