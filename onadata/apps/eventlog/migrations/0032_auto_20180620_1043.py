# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0031_auto_20180601_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='celerytaskprogress',
            name='file',
            field=models.FileField(null=True, upload_to='celeryFiles', blank=True),
        ),
        migrations.AlterField(
            model_name='fieldsightlog',
            name='type',
            field=models.IntegerField(default=0, choices=[(1, 'User was added as the Organization Admin of Organization Name by Invitor Full Name.'), (2, 'User was added as the Project Manager of Project Name by Invitor Full Name.'), (3, 'User was added as Reviewer of Site Name by Invitor Full Name.'), (4, 'User was added as Site Supervisor of Site Name by Invitor Full Name.'), (5, 'User was assigned as an Organization Admin in Organization Name.'), (6, 'User was assigned as a Project Manager in Project Name.'), (7, 'User was assigned as a Reviewer in Site Name.'), (8, 'User was assigned as a Site Supervisor in Site Name.'), (9, 'User created a new organization named Organization Name'), (10, 'User created a new project named Project Name.'), (11, 'User created a new site named Site Name in Project Name.'), (12, 'User created number + sites in Project Name.'), (13, 'User changed the details of Organization Name.'), (14, 'User changed the details of Project Name.'), (15, 'User changed the details of Site Name.'), (16, 'User submitted a response for Form Type Form Name in Site Name.'), (17, 'User reviewed a response for Form Type Form Name in Site Name.'), (18, 'User assigned a new Form Type Form Name in Project Name.'), (19, 'User assigned a new Form Type Form Name to Site Name.'), (20, 'User edited Form Name form.'), (21, 'User assign successful in organization.'), (22, 'User assign sucessfull in project.'), (23, 'Users were already assigned.'), (24, 'User was added as unassigned.'), (25, 'User was added as donor in project.'), (26, 'User was added as the Project Manager in count project of org by Invitor Full Name.'), (27, 'User was added as Reviewer in count site of project by Invitor Full Name.'), (28, 'User was added as Site Supervisor in count site of project by Invitor Full Name.'), (29, 'Project SIte Import From Project Name Completed SuccessFully'), (30, 'Project SIte Import From number of region in Project Name Completed SuccessFully'), (31, 'User edited a response for Form Type Form Name in Site Name.'), (32, 'Report generated sucessfull.'), (412, 'Bulk upload of number + sites in Project Name failed.'), (421, 'User assign unsuccessful in organization.'), (422, 'User assign unsucessfull in project.'), (429, 'Project SIte Import From Project Name Completed SuccessFully'), (430, 'Project SIte Import From number of region in Project Name Completed SuccessFully'), (432, 'Report generation failed.')]),
        ),
    ]
