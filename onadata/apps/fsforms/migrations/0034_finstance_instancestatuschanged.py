# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0013_blueprints'),
        ('logger', '0005_remove_xform_site'),
        ('fsforms', '0033_remove_formgroup_shared_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='FInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('form_status', models.IntegerField(default=0, choices=[(0, b'Outstanding'), (1, b'Rejected'), (2, b'Flagged'), (3, b'Approved')])),
                ('instance', models.OneToOneField(related_name='fieldsight_instance', to='logger.Instance')),
                ('project', models.ForeignKey(related_name='project_instances', to='fieldsight.Site', null=True)),
                ('project_fxf', models.ForeignKey(related_name='project_form_instances', to='fsforms.FieldSightXF', null=True)),
                ('site', models.ForeignKey(related_name='site_instances', to='fieldsight.Site', null=True)),
                ('site_fxf', models.ForeignKey(related_name='site_form_instances', to='fsforms.FieldSightXF', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InstanceStatusChanged',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField(null=True, blank=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('old_status', models.IntegerField(default=0, choices=[(0, b'Outstanding'), (1, b'Rejected'), (2, b'Flagged'), (3, b'Approved')])),
                ('new_status', models.IntegerField(default=0, choices=[(0, b'Outstanding'), (1, b'Rejected'), (2, b'Flagged'), (3, b'Approved')])),
                ('finstance', models.ForeignKey(related_name='comments', to='fsforms.FInstance')),
            ],
        ),
    ]
