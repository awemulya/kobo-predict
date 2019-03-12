# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stripe_cust_id', models.CharField(max_length=300)),
                ('user', models.OneToOneField(related_name='customer', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stripe_sub_id', models.CharField(max_length=300)),
                ('is_active', models.BooleanField(default=False)),
                ('initiated_on', models.DateTimeField()),
                ('terminated_on', models.DateTimeField(null=True, blank=True)),
                ('plan', models.IntegerField(default=0, choices=[(0, b'Free'), (1, b'Basic Monthly'), (2, b'Basic Yearly'), (3, b'Extended Monthly'), (4, b'Extended Yearly'), (5, b'Pro Monthly'), (6, b'Pro Yearly'), (7, b'Scale Monthly'), (8, b'Scale Yearly')])),
                ('stripe_customer', models.ForeignKey(related_name='subscriptions', to='subscriptions.Customer')),
            ],
        ),
    ]
