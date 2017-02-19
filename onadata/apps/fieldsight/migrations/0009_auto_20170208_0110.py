# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0008_auto_20170202_0133'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organization',
            options={'ordering': ['-is_active', 'name']},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['-is_active', 'name']},
        ),
        migrations.AlterModelOptions(
            name='site',
            options={'ordering': ['-is_active', 'name']},
        ),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(max_length=255, verbose_name=b'Organization Name'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='phone',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Contact Number', blank=True),
        ),
    ]
