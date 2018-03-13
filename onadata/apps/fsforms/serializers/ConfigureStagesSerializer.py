from __future__ import unicode_literals
import json

from rest_framework import serializers

from onadata.apps.fieldsight.models import Project, Site
from onadata.apps.fsforms.models import Stage, FieldSightXF
from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import EMSerializer
from onadata.apps.fsforms.serializers.InstanceStatusChangedSerializer import FSXFSerializer
from onadata.apps.logger.models import XForm


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



class SubStageDetailSerializer(serializers.ModelSerializer):
    stage_forms = FSXFSerializer(read_only=True)
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
        fields = ('weight', 'name', 'description', 'id', 'order', 'date_created', 'em', 'responses_count', 'stage_forms')

    def create(self, validated_data):
        stage_id = self.context['kwargs'].get('stage_id')
        tags = self.context['request'].data.get('tags')
        xf = self.context['request'].data.get('xf', {})
        xf_id = xf.get('id', False)
        xform = False
        if xf_id:
            xform = XForm.objects.get(pk=xf_id)


        stage = super(SubStageDetailSerializer, self).create(validated_data)
        main_stage = Stage.objects.get(pk=stage_id)
        if xform:
            fieldsight_form = FieldSightXF.objects.create(xf=xform, site=main_stage.site,
                                                      project=main_stage.project, is_staged=True, stage=stage)
        stage.stage = main_stage
        stage.save()
        return stage


    def update(self,instance,  validated_data):
        stage = super(SubStageDetailSerializer, self).update(instance, validated_data)
        # stage.forms = Stage.objects.get(pk=stage_id)
        # stage.educattionmateruil = Stage.objects.get(pk=stage_id)
        # stage.weight and tag
        return stage



