from django.db import transaction
from rest_framework import serializers

from onadata.apps.fsforms.models import Stage, FieldSightXF


class SubStageSerializer1(serializers.ModelSerializer):
    xf = serializers.CharField()
    form_name = serializers.SerializerMethodField('get_assigned_form_name', read_only=True)
    form = serializers.SerializerMethodField('get_assigned_form', read_only=True)

    class Meta:
        model = Stage
        exclude = ('shared_level', 'site', 'group', 'ready', 'project','stage')

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
    parent = SubStageSerializer1(many=True)

    class Meta:
        model = Stage
        exclude = ('shared_level', 'group', 'ready', 'stage')

    def create(self, validated_data):
        id = self.context['request'].data.get('id', False)
        with transaction.atomic():
            new_substages = validated_data.pop('parent')
            substages_data = self.context['request'].data.get('parent')
            if not id:
                stage = Stage.objects.create(**validated_data)
                for order, ss in enumerate(new_substages):
                    xf = ss.pop('xf')
                    ss.update({'stage':stage, 'order':order+1})
                    sub_stage_obj = Stage.objects.create(**ss)
                    FieldSightXF.objects.create(xf_id=xf,site=stage.site, project=stage.project, is_staged=True, stage=sub_stage_obj)

            else:
                Stage.objects.filter(pk=id).update(**validated_data)
                stage = Stage.objects.get(pk=id)
                for order, sub_stage_data in enumerate(substages_data):
                    old_substage = sub_stage_data.get('id', False)
                    if old_substage:
                        sub_id = sub_stage_data.pop('id')
                        xf = sub_stage_data.pop('xf')
                        sub_stage_data.update({'stage':stage,'order':order+1})
                        Stage.objects.filter(pk=sub_id).update(**sub_stage_data)
                    #     if form change update fxf object's xf
                    else:
                        sub_stage_data.update({'stage':stage,'order':order+1})
                        xf = sub_stage_data.pop('xf')
                        ss = Stage.objects.create(**sub_stage_data)
                        FieldSightXF.objects.create(xf_id=xf,site=stage.site, project=stage.project, is_staged=True,stage=ss)
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

