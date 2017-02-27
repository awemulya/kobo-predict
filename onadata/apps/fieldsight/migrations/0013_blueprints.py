# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import onadata.apps.fieldsight.models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0012_auto_20170216_1141'),
    ]

    operations = [
        migrations.CreateModel(
            name='BluePrints',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=onadata.apps.fieldsight.models.get_image_filename, verbose_name=b'BluePrints')),
                ('site', models.ForeignKey(related_name='blueprints', to='fieldsight.Site')),
            ],
        ),
    ]
