# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0065_auto_20181114_1055'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubmissionOfflineSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('offline_site_id', models.CharField(max_length=20)),
                ('instance', models.OneToOneField(null=True, blank=True, to='fsforms.FInstance')),
            ],
        ),
    ]
