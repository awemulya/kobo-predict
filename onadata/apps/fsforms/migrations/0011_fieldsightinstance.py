# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logger', '0005_remove_xform_site'),
        ('fsforms', '0010_auto_20161117_0348'),
    ]

    operations = [
        migrations.CreateModel(
            name='FieldsightInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fsxform', models.ForeignKey(related_name='fs_instances', to='fsforms.FieldSightXF', null=True)),
                ('instance', models.ForeignKey(related_name='fs_instances', to='logger.Instance', null=True)),
            ],
            options={
                'ordering': ('-fsxform',),
                'db_table': 'fieldsight_forms_instance',
                'verbose_name': 'FSInstance',
                'verbose_name_plural': 'FSInstances',
            },
        ),
    ]
