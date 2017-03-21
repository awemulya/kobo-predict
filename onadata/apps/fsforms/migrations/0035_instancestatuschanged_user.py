# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fsforms', '0034_finstance_instancestatuschanged'),
    ]

    operations = [
        migrations.AddField(
            model_name='instancestatuschanged',
            name='user',
            field=models.ForeignKey(related_name='submission_comments', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
