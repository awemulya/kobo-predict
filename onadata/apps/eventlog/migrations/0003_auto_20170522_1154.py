# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eventlog', '0002_auto_20170522_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightlog',
            name='source',
            field=models.ForeignKey(related_name='log', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='fieldsightlog',
            name='type',
            field=models.IntegerField(default=0, choices=[(0, b'USER'), (1, b'FORM'), (2, b'SUBMISSION'), (3, b'Site')]),
        ),
    ]
