# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0056_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sitetype',
            options={'ordering': ['-identifier']},
        ),
        migrations.AddField(
            model_name='sitetype',
            name='identifier',
            field=models.IntegerField(default=0, verbose_name='ID'),
            preserve_default=False,
        ),
    ]
