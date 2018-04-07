# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0054_remove_site_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='type',
            field=models.ForeignKey(related_name='sites', verbose_name='Type of Site', blank=True, to='fieldsight.SiteType', null=True),
        ),
    ]
