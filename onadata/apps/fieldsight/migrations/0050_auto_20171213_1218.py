# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0049_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='identifier',
            field=models.CharField(max_length=255, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='region',
            unique_together=set([('identifier', 'project')]),
        ),
    ]
