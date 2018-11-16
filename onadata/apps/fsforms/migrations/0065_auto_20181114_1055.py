# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0064_auto_20181111_1421'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='xformhistory',
            unique_together=set([('xform', 'version')]),
        ),
    ]
