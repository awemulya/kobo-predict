# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0040_fieldsightxf_is_deleted'),
    ]

    operations = [
        migrations.CreateModel(
            name='EducationalImages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'education-material-images', verbose_name=b'Education Images')),
            ],
        ),
        migrations.CreateModel(
            name='EducationMaterial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_pdf', models.BooleanField(default=False)),
                ('pdf', models.FileField(null=True, upload_to=b'education-material-pdf', blank=True)),
                ('title', models.CharField(max_length=31, null=True, blank=True)),
                ('text', models.TextField(null=True, blank=True)),
                ('stage', models.OneToOneField(related_name='em', to='fsforms.Stage')),
            ],
        ),
        migrations.AlterField(
            model_name='fieldsightxf',
            name='form_status',
            field=models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Rejected'), (2, b'Flagged'), (3, b'Approved')]),
        ),
        migrations.AlterField(
            model_name='finstance',
            name='form_status',
            field=models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Rejected'), (2, b'Flagged'), (3, b'Approved')]),
        ),
        migrations.AlterField(
            model_name='instancestatuschanged',
            name='new_status',
            field=models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Rejected'), (2, b'Flagged'), (3, b'Approved')]),
        ),
        migrations.AlterField(
            model_name='instancestatuschanged',
            name='old_status',
            field=models.IntegerField(default=0, choices=[(0, b'Pending'), (1, b'Rejected'), (2, b'Flagged'), (3, b'Approved')]),
        ),
        migrations.AddField(
            model_name='educationalimages',
            name='educational_material',
            field=models.ForeignKey(related_name='em_images', to='fsforms.EducationMaterial'),
        ),
    ]
