from __future__ import unicode_literals
import json

from django.db import transaction
from rest_framework import serializers

from onadata.apps.fieldsight.models import Project, Site
from onadata.apps.fsforms.models import Stage, FieldSightXF
from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import EMSerializer
from onadata.apps.fsforms.serializers.InstanceStatusChangedSerializer import FSXFSerializer


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


class SubStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ('name', 'description', 'id', 'order')

    def create(self, validated_data):
        stage_id = self.context['kwargs'].get('stage_id')
        stage = super(SubStageSerializer, self).create(validated_data)
        stage.parent = Stage.objects.get(pk=stage_id)
        return stage


class SubStageDetailSerializer(serializers.ModelSerializer):
    stage_forms = FSXFSerializer()
    em = EMSerializer(read_only=True)
    responses_count = serializers.SerializerMethodField()

    def get_responses_count(self, obj):
        try:
            fsxf = FieldSightXF.objects.get(stage=obj)
            if fsxf.site is None:
                return fsxf.project_form_instances.count()
            else:
                return fsxf.site_form_instances.count()

        except FieldSightXF.DoesNotExist:
            return 0

    class Meta:
        model = Stage
        fields = ('name', 'description', 'id', 'order', 'date_created', 'em', 'responses_count', 'stage_forms')

    def update(self,instance,  validated_data):
        stage = super(SubStageDetailSerializer, self).update(instance, validated_data)
        # stage.forms = Stage.objects.get(pk=stage_id)
        # stage.educattionmateruil = Stage.objects.get(pk=stage_id)
        # stage.weight and tag
        return stage



