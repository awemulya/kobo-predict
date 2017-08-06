# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0042_stage_project_stage_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstanceImages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'submission-feedback-images', verbose_name=b'Status Changed Images')),
                ('instance_status', models.ForeignKey(related_name='images', to='fsforms.InstanceStatusChanged')),
            ],
        ),
    ]
