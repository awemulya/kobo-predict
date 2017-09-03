# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0023_auto_20170829_1558'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eventlog', '0013_auto_20170822_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightlog',
            name='project',
            field=models.ForeignKey(related_name='logs', to='fieldsight.Project', null=True),
        ),
        migrations.AddField(
            model_name='fieldsightlog',
            name='seen_by',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='fieldsightlog',
            name='site',
            field=models.ForeignKey(related_name='logs', to='fieldsight.Site', null=True),
        ),
        migrations.AlterField(
            model_name='fieldsightlog',
            name='type',
            field=models.IntegerField(default=0, choices=[(0, b'User joined Organization Name as an Organization Admin.'), (1, b'User was added as the Project Manager of Project Name by Invitor Full Name.'), (2, b'User was added as Reviewer of Site Name by Invitor Full Name.'), (3, b'User was added as Site Supervisor of Site Name by Invitor Full Name.'), (4, b'User was assigned as an Organization Admin in Organization Name.'), (5, b'User was assigned as a Project Manager in Project Name.'), (6, b'User was assigned as a Reviewer in Site Name.'), (7, b'User was assigned as a Site Supervisor in Site Name.'), (8, b'User created a new organization named Organization Name'), (9, b'User created a new project named Project Name.'), (10, b'User created a new site named Site Name in Project Name.'), (11, b'User created number + sites in Project Name.'), (12, b'User changed the details of Organization Name.'), (13, b'User changed the details of Project Name.'), (14, b'User changed the details of Site Name.'), (15, b'User submitted a response for Form Type Form Name in Site Name.'), (16, b'User reviewed a response for Form Type Form Name in Site Name.'), (17, b'User assigned a new Form Type Form Name in Project Name.'), (18, b'User assigned a new Form Type Form Name to Site Name.'), (19, b'User edited Form Name form.')]),
        ),
    ]
