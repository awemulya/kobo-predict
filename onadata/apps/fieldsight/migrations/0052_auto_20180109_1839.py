# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0051_auto_20171213_1236'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='site',
            options={'ordering': ['-is_active', '-id']},
        ),
        migrations.AlterModelOptions(
            name='timezone',
            options={'ordering': ['time_zone']},
        ),
        migrations.AlterField(
            model_name='organization',
            name='logo',
            field=models.ImageField(default='logo/default_org_image.jpg', upload_to='logo'),
        ),
        migrations.AlterField(
            model_name='project',
            name='logo',
            field=models.ImageField(default='logo/default_project_image.jpg', upload_to='logo'),
        ),
        migrations.AlterField(
            model_name='site',
            name='logo',
            field=models.ImageField(default='logo/default_site_image.png', upload_to='logo'),
        ),
    ]
