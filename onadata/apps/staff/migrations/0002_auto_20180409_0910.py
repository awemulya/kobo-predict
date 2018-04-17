# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='staff',
            name='Account_number',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='staff',
            name='address',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='staff',
            name='bank_name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='staff',
            name='gender',
            field=models.IntegerField(default=1, choices=[(1, b'Male'), (2, b'Female'), (3, b'Other')]),
        ),
        migrations.AddField(
            model_name='staff',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='staff',
            name='phone_number',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='staff',
            name='photo',
            field=models.ImageField(default=b'staffs/default_staff_image.jpg', upload_to=b'staffs'),
        ),
        migrations.AddField(
            model_name='team',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='staff',
            name='type',
            field=models.IntegerField(default=1, choices=[(1, b'Laborer'), (2, b'Worker'), (3, b'Transporter')]),
        ),
    ]
