# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0023_auto_20180204_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldsightlog',
            name='type',
            field=models.IntegerField(default=0, choices=[(1, 'User was added as the Organization Admin of Organization Name by Invitor Full Name.'), (2, 'User was added as the Project Manager of Project Name by Invitor Full Name.'), (3, 'User was added as Reviewer of Site Name by Invitor Full Name.'), (4, 'User was added as Site Supervisor of Site Name by Invitor Full Name.'), (5, 'User was assigned as an Organization Admin in Organization Name.'), (6, 'User was assigned as a Project Manager in Project Name.'), (7, 'User was assigned as a Reviewer in Site Name.'), (8, 'User was assigned as a Site Supervisor in Site Name.'), (9, 'User created a new organization named Organization Name'), (10, 'User created a new project named Project Name.'), (11, 'User created a new site named Site Name in Project Name.'), (12, 'User created number + sites in Project Name.'), (13, 'User changed the details of Organization Name.'), (14, 'User changed the details of Project Name.'), (15, 'User changed the details of Site Name.'), (16, 'User submitted a response for Form Type Form Name in Site Name.'), (17, 'User reviewed a response for Form Type Form Name in Site Name.'), (18, 'User assigned a new Form Type Form Name in Project Name.'), (19, 'User assigned a new Form Type Form Name to Site Name.'), (20, 'User edited Form Name form.'), (24, 'User was added as unassigned.'), (25, 'User was added as donor in project.')]),
        ),
    ]
