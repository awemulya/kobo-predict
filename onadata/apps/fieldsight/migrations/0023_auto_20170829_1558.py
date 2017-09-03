# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fieldsight', '0022_auto_20170823_1928'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinvite',
            name='by_user',
            field=models.ForeignKey(related_name='invited_by_user', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userinvite',
            name='organization',
            field=models.ForeignKey(related_name='invite_organization_roles', to='fieldsight.Organization'),
        ),
    ]
