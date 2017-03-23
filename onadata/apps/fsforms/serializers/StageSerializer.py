from rest_framework import serializers

from onadata.apps.fsforms.models import Stage, FieldSightXF


class SubStageSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Stage
        exclude = ('shared_level', 'site', 'group', 'ready', 'project','stage')


class StageSerializer1(serializers.ModelSerializer):
    parent = SubStageSerializer1(many=True)

    class Meta:
        model = Stage
        exclude = ('shared_level', 'group', 'ready', 'stage')

    def create(self, validated_data):
        id = self.context['request'].data.get('id', False)
        validated_data.pop('parent')
        substages_data = self.context['request'].data.get('parent')
        if not id:
            stage = Stage.objects.create(**validated_data)
        else:
            Stage.objects.filter(pk=id).update(**validated_data)
            stage = Stage.objects.get(pk=id)
        for sub_stage_data in substages_data:
            sub_id = sub_stage_data.pop('id')
            if not sub_id:
                stage = Stage.objects.create(**sub_stage_data)
            else:
                Stage.objects.filter(pk=sub_id).update(**sub_stage_data)
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

