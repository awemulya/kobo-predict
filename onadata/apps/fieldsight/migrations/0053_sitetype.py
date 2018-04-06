# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0052_auto_20180109_1839'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name='Type')),
                ('project', models.ForeignKey(related_name='types', to='fieldsight.Project')),
            ],
        ),
    ]
