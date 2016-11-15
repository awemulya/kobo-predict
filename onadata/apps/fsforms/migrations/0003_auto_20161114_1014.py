# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0002_auto_20161108_0034'),
        ('fsforms', '0002_auto_20161114_0443'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fieldsightxf',
            options={'ordering': ('-date_created',), 'verbose_name': 'XForm', 'verbose_name_plural': 'XForms'},
        ),
        migrations.RemoveField(
            model_name='fieldsightxf',
            name='site',
        ),
        migrations.AddField(
            model_name='fieldsightxf',
            name='site',
            field=models.ForeignKey(related_name='site_forms', blank=True, to='fieldsight.Site', null=True),
        ),
    ]
