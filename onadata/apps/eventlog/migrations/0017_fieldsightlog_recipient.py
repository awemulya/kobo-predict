# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eventlog', '0016_auto_20170906_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightlog',
            name='recipient',
            field=models.ForeignKey(related_name='recipent_log', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
