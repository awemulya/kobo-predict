# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20170202_0133'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='google_talk',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='hike',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='line',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='office_number',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='primary_number',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='qq',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='secondary_number',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='tango',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='twitter',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='viber',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='wechat',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='whatsapp',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='address',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='skype',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
    ]
