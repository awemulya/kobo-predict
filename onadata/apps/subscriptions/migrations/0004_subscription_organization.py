# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0070_merge'),
        ('subscriptions', '0003_auto_20190315_1143'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='organization',
            field=models.OneToOneField(related_name='subscription', null=True, blank=True, to='fieldsight.Organization'),
        ),
    ]
