# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fieldsight', '0065_auto_20180903_1514'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestOrganizationStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_approve', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('by_user', models.ForeignKey(related_name='request_organization_by', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(related_name='request_org_status', to='fieldsight.Organization')),
                ('to_user', models.ForeignKey(related_name='request_organization_to', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
