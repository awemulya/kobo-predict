# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fieldsight', '0002_auto_20161108_0034'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('started_at', models.DateTimeField(default=datetime.datetime.now)),
                ('ended_at', models.DateTimeField(null=True, blank=True)),
                ('group', models.ForeignKey(to='auth.Group')),
                ('organization', models.ForeignKey(related_name='organization_roles', blank=True, to='fieldsight.Organization', null=True)),
                ('project', models.ForeignKey(related_name='project_roles', blank=True, to='fieldsight.Project', null=True)),
                ('site', models.ForeignKey(related_name='site_roles', blank=True, to='fieldsight.Site', null=True)),
                ('user', models.ForeignKey(related_name='user_roles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='userrole',
            unique_together=set([('user', 'group', 'organization', 'project', 'site')]),
        ),
    ]
