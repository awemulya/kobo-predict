# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0002_auto_20180409_0910'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bank_name', models.CharField(max_length=255, null=True, blank=True)),
            ],
        ),
        migrations.RenameField(
            model_name='staff',
            old_name='Account_number',
            new_name='account_number',
        ),
        migrations.RenameField(
            model_name='staff',
            old_name='full_name',
            new_name='ethnicity',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='type',
        ),
        migrations.AddField(
            model_name='staff',
            name='contract_end',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='staff',
            name='contract_start',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='staff',
            name='designation',
            field=models.IntegerField(default=1, choices=[(1, b'TSC Agent'), (2, b'Social Mobilizer'), (3, b'Junior Builder-Trainer'), (4, b'Junior Builder-Trainer')]),
        ),
        migrations.AddField(
            model_name='staff',
            name='first_name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='staff',
            name='last_name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='staff',
            name='bank',
            field=models.ForeignKey(blank=True, to='staff.Bank', null=True),
        ),
    ]
