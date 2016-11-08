# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userrole',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='userrole',
            name='group',
        ),
        migrations.RemoveField(
            model_name='userrole',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='userrole',
            name='project',
        ),
        migrations.RemoveField(
            model_name='userrole',
            name='site',
        ),
        migrations.RemoveField(
            model_name='userrole',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserRole',
        ),
    ]
