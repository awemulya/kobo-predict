# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0003_auto_20161105_0652'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='additional_desc',
            field=models.TextField(null=True, verbose_name=b'Additional Description', blank=True),
        ),
        migrations.AddField(
            model_name='site',
            name='public_desc',
            field=models.TextField(null=True, verbose_name=b'Public Description', blank=True),
        ),
        migrations.AddField(
            model_name='site',
            name='type',
            field=models.ForeignKey(default=1, verbose_name=b'Type of Site', to='fieldsight.ProjectType'),
            preserve_default=False,
        ),
    ]
