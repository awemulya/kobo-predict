from django.db import transaction
from rest_framework import serializers

from onadata.apps.fsforms.models import Stage, FieldSightXF
from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import FSXFSerializer
from onadata.apps.logger.models import XForm


class SubStageSerializer1(serializers.ModelSerializer):
    stage_forms = FSXFSerializer()

    class Meta:
        model = Stage
        exclude = ('shared_level', 'site', 'group', 'ready', 'project','stage', 'date_modified', 'date_created')

    def get_assigned_form(self, obj):
        if not FieldSightXF.objects.filter(stage=obj).exists():
            return None
        else:
            fsxf = FieldSightXF.objects.get(stage=obj)
            if fsxf.xf:
                return fsxf.id
        return None

    def get_assigned_form_name(self, obj):
        if not FieldSightXF.objects.filter(stage=obj).exists():
            return None
        else:
            fsxf = FieldSightXF.objects.get(stage=obj)
            if fsxf.xf:
                return fsxf.xf.title
        return None

    def get_assigned_form(self, obj):
        if not FieldSightXF.objects.filter(stage=obj).exists():
            return None
        else:
            fsxf = FieldSightXF.objects.get(stage=obj)
            if fsxf.xf:
                return fsxf.id
        return None


class StageSerializer1(serializers.ModelSerializer):
    parent = SubStageSerializer1(many=True, read_only=True)

    class Meta:
        model = Stage
        exclude = ('shared_level', 'group', 'ready', 'stage')

    def create(self, validated_data):
        id = self.context['request'].data.get('id', False)
        with transaction.atomic():
            substages_data = self.context['request'].data.get('parent')
            if not id:
                stage = Stage.objects.create(**validated_data)
                for order, ss in enumerate(substages_data):
                    fxf = ss.pop('stage_forms')
                    xf = fxf.get('xf')
                    xf_id = xf.get('id')
                    # fxf_id = fxf.get('id')
                    ss.pop('id')

                    ss.update({'stage':stage, 'order':order+1})
                    sub_stage_obj = Stage.objects.create(**ss)
                    FieldSightXF.objects.create(xf_id=xf_id,site=stage.site, project=stage.project, is_staged=True, stage=sub_stage_obj)

            else:
                Stage.objects.filter(pk=id).update(**validated_data)
                stage = Stage.objects.get(pk=id)
                for order, sub_stage_data in enumerate(substages_data):
                    old_substage = sub_stage_data.get('id', "")
                    if old_substage:
                        sub_id = sub_stage_data.pop('id')
                        fxf = sub_stage_data.pop('stage_forms')
                        sub_stage_data.update({'stage':stage,'order':order+1})
                        Stage.objects.filter(pk=sub_id).update(**sub_stage_data)
                        sub_stage = Stage.objects.get(pk=sub_id)
                        old_fsxf = sub_stage.stage_forms
                        old_xf = old_fsxf.xf

                        xf = fxf.get('xf')
                        xf_id = xf.get('id')
                        if old_xf.id  != xf_id:
                            # xform changed
                            old_fsxf.xf = XForm.objects.get(pk=xf_id)
                            old_fsxf.save()
                        #     notify mobile and web

                    #     if form change update fxf object's xf
                    else:
                        fxf = sub_stage_data.pop('stage_forms')
                        xf = fxf.get('xf')
                        xf_id = xf.get('id')
                        # fxf_id = fxf.get('id')
                        sub_stage_data.pop('id')

                        sub_stage_data.update({'stage':stage, 'order':order+1})
                        sub_stage_obj = Stage.objects.create(**sub_stage_data)
                        FieldSightXF.objects.create(xf_id=xf_id,site=stage.site, project=stage.project, is_staged=True, stage=sub_stage_obj)
            return stage


class StageSerializer(serializers.ModelSerializer):
    main_stage = serializers.ReadOnlyField(source='stage.name', read_only=True)

    class Meta:
        model = Stage
        fields = ('name', 'description', 'id', 'stage', 'main_stage', 'order', 'site')


class SubStageSerializer(serializers.ModelSerializer):
    main_stage = serializers.ReadOnlyField(source='stage.name', read_only=True)
    form = serializers.SerializerMethodField('get_assigned_form', read_only=True)

    class Meta:
        model = Stage
        fields = ('name', 'description', 'id', 'stage', 'main_stage', 'order', 'site', 'form')

    def get_assigned_form(self, obj):
        if not FieldSightXF.objects.filter(stage=obj).exists():
            return None
        else:
            fsxf = FieldSightXF.objects.get(stage=obj)
            if fsxf.xf:
                return fsxf.id
        return None

