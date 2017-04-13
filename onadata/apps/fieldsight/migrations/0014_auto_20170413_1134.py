# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import onadata.apps.fieldsight.models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0013_blueprints'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteCreateSurveyImages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=onadata.apps.fieldsight.models.get_survey_image_filename, verbose_name=b'survey images')),
            ],
        ),
        migrations.AddField(
            model_name='site',
            name='is_survey',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sitecreatesurveyimages',
            name='site',
            field=models.ForeignKey(related_name='create_surveys', to='fieldsight.Site'),
        ),
    ]
