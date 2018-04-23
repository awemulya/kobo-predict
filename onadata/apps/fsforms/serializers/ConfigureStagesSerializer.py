import json

from rest_framework import serializers

from onadata.apps.fieldsight.models import Project, Site
from onadata.apps.fsforms.models import Stage, FieldSightXF, EducationalImages, EducationMaterial
from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import EMSerializer
from onadata.apps.fsforms.serializers.InstanceStatusChangedSerializer import FSXFSerializer
from onadata.apps.logger.models import XForm


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ('name', 'description', 'id', 'order', 'tags')

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

    # def update(self, instance, validated_data):
    #     tags = self.context['request'].data.get('tags', [])
    #     stage = super(StageSerializer, self).update(instance, validated_data)
    #     import ipdb
    #     ipdb.set_trace()
    #
    #     return stage


class SubStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ('name', 'description', 'id', 'order', 'tags')


class SubStageDetailSerializer(serializers.ModelSerializer):
    stage_forms = FSXFSerializer(read_only=True)
    em = EMSerializer(read_only=True)
    responses_count = serializers.SerializerMethodField()
    has_stage = serializers.SerializerMethodField()
    has_em = serializers.SerializerMethodField()
    is_deployed = serializers.SerializerMethodField()

    def get_responses_count(self, obj):
        try:
            fsxf = FieldSightXF.objects.get(stage=obj)
            if fsxf.site is None:
                return fsxf.project_form_instances.count()
            else:
                return fsxf.site_form_instances.count()

        except FieldSightXF.DoesNotExist:
            return 0
    def get_has_stage(self, obj):
        try:
            obj.stage_forms
            return True
        except:
            return False

    def get_has_em(self, obj):
        try:
            obj.em
            return True
        except:
            return False

    def get_is_deployed(self, obj):
        try:
            return obj.stage_forms.is_deployed
        except:
            return False
    class Meta:
        model = Stage
        fields = ('weight', 'name', 'description', 'id', 'order', 'date_created', 'em', 'responses_count',
                  'stage_forms', 'has_stage', 'has_em', 'tags', 'is_deployed')

    def create(self, validated_data):
        stage_id = self.context['kwargs'].get('stage_id')
        xf = self.context['request'].data.get('xf', {})
        xform = False
        if xf and xf != '':
            xf_id = xf.get('id', False)
            if xf_id:
                xform = XForm.objects.get(pk=xf_id)


        stage = super(SubStageDetailSerializer, self).create(validated_data)
        main_stage = Stage.objects.get(pk=stage_id)
        if xform:
            FieldSightXF.objects.create(xf=xform, site=main_stage.site,
                                                      project=main_stage.project, is_staged=True, stage=stage)
        stage.stage = main_stage
        stage.save()
        # tags
        return stage

    def update(self,instance, validated_data):
        xf = self.context['request'].data.get('xf', {})
        xform = False
        if xf and xf != '':
            xf_id = xf.get('id', False)
            if xf_id:
                xform = XForm.objects.get(pk=xf_id)
        stage = super(SubStageDetailSerializer, self).update(instance, validated_data)
        if xform:
            try:
                old_form = stage.stage_forms
                if old_form.xf.id == xform.id:
                    pass
                else:
                    old_form.deleted = True
                    old_form.stage = None
                    old_form.save()
                    FieldSightXF.objects.create(xf=xform, site=stage.site,
                                                  project=stage.project, is_staged=True, stage=stage)
            except:
                if xform:
                    FieldSightXF.objects.create(xf=xform, site=stage.site,
                                                      project=stage.project, is_staged=True, stage=stage)
        # tags
        return stage


class EMImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalImages
        exclude = ("educational_material",)


class EMSerializer(serializers.ModelSerializer):
    em_images = EMImagesSerializer(many=True, read_only=True)

    class Meta:
        model = EducationMaterial
        exclude = ()