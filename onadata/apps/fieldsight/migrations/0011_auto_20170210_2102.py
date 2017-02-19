# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0010_site_identifier'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='site',
            unique_together=set([('identifier', 'project')]),
        ),
    ]
