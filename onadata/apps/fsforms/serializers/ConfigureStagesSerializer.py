from __future__ import unicode_literals
import json

from django.db import transaction
from rest_framework import serializers

from onadata.apps.fieldsight.models import Project, Site
from onadata.apps.fsforms.models import Stage


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ('name', 'description', 'id', 'order')

    def create(self, validated_data):
        pk = self.context['kwargs'].get('pk')
        is_project = self.context['kwargs'].get('is_project')
        stage = super(StageSerializer, self).create(validated_data)
        if is_project:
            stage.project = Project.objects.get(pk=pk)
        else:
            stage.site = Site.objects.get(pk=pk)
        stage.save()
        return stage



