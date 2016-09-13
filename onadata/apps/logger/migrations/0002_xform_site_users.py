# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('logger', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='xform',
            name='site_users',
            field=models.ManyToManyField(related_name='myforms', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
