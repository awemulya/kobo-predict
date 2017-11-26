# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0026_region'),
    ]

    operations = [
        migrations.CreateModel(
            name='Timezone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('city', models.CharField(max_length=255)),
                ('offset_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='organization',
            name='logo',
            field=models.ImageField(upload_to='logo'),
        ),
        migrations.AlterField(
            model_name='project',
            name='logo',
            field=models.ImageField(upload_to='logo'),
        ),
        migrations.AlterField(
            model_name='site',
            name='logo',
            field=models.ImageField(upload_to='logo'),
        ),
    ]
