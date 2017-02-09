# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0009_auto_20170208_0110'),
        ('logger', '0005_remove_xform_site'),
        ('fsforms', '0025_auto_20170208_0110'),
    ]

    operations = [
        migrations.CreateModel(
            name='FieldSightFormLibrary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_global', models.BooleanField(default=False)),
                ('shared_date', models.DateTimeField(auto_now=True)),
                ('organization', models.ForeignKey(blank=True, to='fieldsight.Organization', null=True)),
                ('project', models.ForeignKey(blank=True, to='fieldsight.Project', null=True)),
                ('xf', models.ForeignKey(to='logger.XForm')),
            ],
        ),
    ]
