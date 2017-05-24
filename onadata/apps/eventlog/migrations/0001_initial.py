# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20170206_0059'),
        ('fsforms', '0039_finstance_submitted_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='FieldSightLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(default=0, choices=[(0, b'USER'), (1, b'FORM'), (2, b'SUBMISSION')])),
                ('title', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('form', models.ForeignKey(related_name='log', to='fsforms.FieldSightXF', null=True)),
                ('instance', models.ForeignKey(related_name='log', to='fsforms.FInstance', null=True)),
                ('profile', models.ForeignKey(related_name='log', to='users.UserProfile', null=True)),
            ],
            options={
                'ordering': ['-date', 'type'],
                'get_latest_by': 'date',
            },
        ),
    ]
