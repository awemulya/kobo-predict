# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0007_auto_20161214_0334'),
        ('users', '0004_auto_20161218_0335'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='organization',
            field=models.ForeignKey(blank=True, to='fieldsight.Organization', null=True),
        ),
    ]
