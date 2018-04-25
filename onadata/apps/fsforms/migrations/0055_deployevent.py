# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0058_auto_20180408_1435'),
        ('fsforms', '0054_stage_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeployEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', jsonfield.fields.JSONField(default={})),
                ('date', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(related_name='deploy_data', to='fieldsight.Project', null=True)),
                ('site', models.ForeignKey(related_name='deploy_data', to='fieldsight.Site', null=True)),
            ],
        ),
    ]
