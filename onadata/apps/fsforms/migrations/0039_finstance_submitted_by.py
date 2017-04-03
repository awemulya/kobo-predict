# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fsforms', '0038_auto_20170324_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='finstance',
            name='submitted_by',
            field=models.ForeignKey(related_name='supervisor', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
