# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('fieldsight', '0017_userinvites'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInvite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=255)),
                ('reg_status', models.BooleanField(default=False)),
                ('group', models.ForeignKey(to='auth.Group')),
                ('organization', models.ForeignKey(related_name='invite_organization_roles', blank=True, to='fieldsight.Organization', null=True)),
                ('project', models.ForeignKey(related_name='invite_project_roles', blank=True, to='fieldsight.Project', null=True)),
                ('site', models.ForeignKey(related_name='invite_site_roles', blank=True, to='fieldsight.Site', null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='userinvites',
            name='group',
        ),
        migrations.RemoveField(
            model_name='userinvites',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='userinvites',
            name='project',
        ),
        migrations.RemoveField(
            model_name='userinvites',
            name='site',
        ),
        migrations.DeleteModel(
            name='UserInvites',
        ),
    ]
