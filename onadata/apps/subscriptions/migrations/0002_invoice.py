# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField()),
                ('amount', models.FloatField()),
                ('quantity', models.IntegerField()),
                ('overage', models.IntegerField(default=0)),
                ('roll_over', models.IntegerField(default=0)),
                ('customer', models.ForeignKey(related_name='invoices', to='subscriptions.Customer')),
            ],
        ),
    ]
