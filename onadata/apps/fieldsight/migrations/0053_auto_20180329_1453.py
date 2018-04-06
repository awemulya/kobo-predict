# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0052_auto_20180109_1839'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinvite',
            name='project',
        ),
        migrations.AddField(
            model_name='userinvite',
            name='project',
            field=models.ManyToManyField(related_name='invite_project_roles', null=True, to='fieldsight.Project', blank=True),
        ),
        migrations.RemoveField(
            model_name='userinvite',
            name='site',
        ),
        migrations.AddField(
            model_name='userinvite',
            name='site',
            field=models.ManyToManyField(related_name='invite_site_roles', null=True, to='fieldsight.Site', blank=True),
        ),
    ]
