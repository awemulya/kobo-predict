# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0001_initial'),
        ('logger', '0003_remove_xform_site_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='xform',
            name='site',
            field=models.ManyToManyField(related_name='site_forms', to='fieldsight.Site', blank=True),
        ),
    ]
