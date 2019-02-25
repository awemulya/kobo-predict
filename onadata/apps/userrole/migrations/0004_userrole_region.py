# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0065_auto_20180903_1514'),
        ('userrole', '0003_userrole_staff_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrole',
            name='region',
            field=models.ForeignKey(related_name='region_roles', blank=True, to='fieldsight.Region', null=True),
        ),
    ]
