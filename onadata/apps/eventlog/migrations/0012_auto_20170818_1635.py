# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0011_auto_20170807_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldsightlog',
            name='type',
            field=models.IntegerField(default=0, choices=[(0, b'USER'), (1, b'FORM'), (2, b'SUBMISSION'), (3, b'Site'), (4, b'Project'), (5, b'Organization'), (6, b'Role'), (7, b'XFORM'), (8, b'SUBMISSION_STATUS'), (9, b'USER_INVITE')]),
        ),
    ]
