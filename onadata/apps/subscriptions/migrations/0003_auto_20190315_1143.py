# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0002_invoice'),
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('plan', models.IntegerField(default=0, choices=[(0, b'Free'), (1, b'Basic Monthly'), (2, b'Basic Yearly'), (3, b'Extended Monthly'), (4, b'Extended Yearly'), (5, b'Pro Monthly'), (6, b'Pro Yearly'), (7, b'Scale Monthly'), (8, b'Scale Yearly')])),
                ('submissions', models.IntegerField()),
                ('extra_submissions_charge', models.IntegerField(default=0)),
            ],
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='plan',
        ),
        migrations.AddField(
            model_name='subscription',
            name='package',
            field=models.ForeignKey(related_name='subscriptions', blank=True, to='subscriptions.Package', null=True),
        ),
    ]
