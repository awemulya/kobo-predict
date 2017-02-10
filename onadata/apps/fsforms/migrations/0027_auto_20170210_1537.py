# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0026_fieldsightformlibrary'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fieldsightformlibrary',
            options={'ordering': ('-shared_date',), 'verbose_name': 'Library', 'verbose_name_plural': 'Library'},
        ),
        migrations.AlterField(
            model_name='schedule',
            name='selected_days',
            field=models.ManyToManyField(related_name='days', to='fsforms.Days', blank=True),
        ),
    ]
