# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0015_auto_20170906_1211'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightlog',
            name='extra_message',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='fieldsightlog',
            name='type',
            field=models.IntegerField(default=0, choices=[(1, b'User was added as the Organization Admin of Organization Name by Invitor Full Name.'), (2, b'User was added as the Project Manager of Project Name by Invitor Full Name.'), (3, b'User was added as Reviewer of Site Name by Invitor Full Name.'), (4, b'User was added as Site Supervisor of Site Name by Invitor Full Name.'), (5, b'User was assigned as an Organization Admin in Organization Name.'), (6, b'User was assigned as a Project Manager in Project Name.'), (7, b'User was assigned as a Reviewer in Site Name.'), (8, b'User was assigned as a Site Supervisor in Site Name.'), (9, b'User created a new organization named Organization Name'), (10, b'User created a new project named Project Name.'), (11, b'User created a new site named Site Name in Project Name.'), (12, b'User created number + sites in Project Name.'), (13, b'User changed the details of Organization Name.'), (14, b'User changed the details of Project Name.'), (15, b'User changed the details of Site Name.'), (16, b'User submitted a response for Form Type Form Name in Site Name.'), (17, b'User reviewed a response for Form Type Form Name in Site Name.'), (18, b'User assigned a new Form Type Form Name in Project Name.'), (19, b'User assigned a new Form Type Form Name to Site Name.'), (20, b'User edited Form Name form.')]),
        ),
    ]
