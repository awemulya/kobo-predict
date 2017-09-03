# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0019_userinvite_new_invite'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinvite',
            name='token',
            field=models.CharField(default='sdsdsdaa234rerdsfs', max_length=255),
            preserve_default=False,
        ),
    ]
