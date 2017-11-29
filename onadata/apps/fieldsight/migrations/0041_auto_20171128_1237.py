# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0040_project_region'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='region',
            new_name='cluster_sites_by_region',
        ),
    ]
