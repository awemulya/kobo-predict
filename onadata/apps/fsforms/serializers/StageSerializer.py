import json

from django.db import transaction
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from onadata.apps.fsforms.models import Stage, FieldSightXF, EducationMaterial, EducationalImages
from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import FSXFSerializer
from channels import Group as ChannelGroup


class EMImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalImages
        exclude = ("educational_material",)


class EMSerializer(serializers.ModelSerializer):
    em_images = EMImagesSerializer(many=True, read_only=True)
    class Meta:
        model = EducationMaterial
        exclude = ('stage','fsxf')

class SubStageSerializer1(serializers.ModelSerializer):
    stage_forms = FSXFSerializer()
    em = EMSerializer(read_only=True)

    class Meta:
        model = Stage
        exclude = ('shared_level', 'site', 'group', 'ready', 'project','stage', 'date_modified', 'date_created',)

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
    # parent = SubStageSerializer1(many=True, read_only=True)
    parent = SerializerMethodField('get_substages')

    class Meta:
        model = Stage
        exclude = ('shared_level', 'group', 'ready', 'stage',)

    def get_substages(self, stage):
        stages = Stage.objects.filter(stage=stage, stage_forms__is_deleted=False)
        serializer = SubStageSerializer1(instance=stages, many=True)
        return serializer.data

    def create(self, validated_data):
        id = self.context['request'].data.get('id', False)
        with transaction.atomic():
            sub_stages_data = self.context['request'].data.get('parent')
            if not id:
                stage = Stage.objects.create(**validated_data)
                for order, ss in enumerate(sub_stages_data):
                    ss.pop('id')
                    fxf = ss.pop('stage_forms')
                    xf_id = fxf['xf']['id']
                    ss.update({'stage':stage, 'order':order+1})
                    sub_stage_obj = Stage.objects.create(**ss)
                    FieldSightXF.objects.create(xf_id=xf_id,site=stage.site, project=stage.project, is_staged=True,
                                                stage=sub_stage_obj)
                    if stage.project:
                        noti = fxf.logs.create(source=self.request.user, type=18, title="Stage",
                                               organization=fxf.project.organization,
                                               project = fxf.project,
                                               description='{0} assigned new Stage form  {1} to {2} '.format(
                                                   self.request.user.get_full_name(),
                                                   fxf.xf.title,
                                                   fxf.project.name
                                               ))
                        result = {}
                        result['description'] = noti.description
                        result['url'] = noti.get_absolute_url()
                        # ChannelGroup("site-{}".format(fxf.site.id)).send({"text": json.dumps(result)})
                        ChannelGroup("project-{}".format(fxf.project.id)).send({"text": json.dumps(result)})
                    else:
                        noti = fxf.logs.create(source=self.request.user, type=19, title="Stage",
                                               organization=fxf.project.organization,
                                               project = fxf.site.project,
                                               site = fxf.site,
                                               description='{0} assigned new Stage form  {1} to {2} '.format(
                                                   self.request.user.get_full_name(),
                                                   fxf.xf.title,
                                                   fxf.project.name
                                               ))
                        result = {}
                        result['description'] = noti.description
                        result['url'] = noti.get_absolute_url()
                        ChannelGroup("site-{}".format(fxf.site.id)).send({"text": json.dumps(result)})
                        ChannelGroup("project-{}".format(fxf.site.project.id)).send({"text": json.dumps(result)})



            else:
                # Stage.objects.filter(pk=id).update(**validated_data)
                stage = Stage.objects.get(pk=id)
                for attr, value in validated_data.items():
                    setattr(stage, attr, value)
                stage.save()
                for order, sub_stage_data in enumerate(sub_stages_data):
                    old_substage = sub_stage_data.get('id', "")
                    if old_substage:
                        sub_id = sub_stage_data.pop('id')
                        fxf = sub_stage_data.pop('stage_forms')
                        sub_stage_data.update({'stage':stage,'order':order+1})
                        sub_stage = Stage.objects.get(pk=sub_id)
                        for attr, value in sub_stage_data.items():
                            setattr(sub_stage, attr, value)
                        sub_stage.save()

                        old_fsxf = sub_stage.stage_forms
                        old_xf = old_fsxf.xf

                        xf = fxf.get('xf')
                        xf_id = xf.get('id')
                        if old_xf.id  != xf_id:
                            # xform changed history and mew fsf
                            old_fsxf.is_deployed = False
                            old_fsxf.is_deleted = True
                            old_fsxf.stage=None
                            old_fsxf.save()
                            #create new fieldsight form
                            FieldSightXF.objects.create(xf_id=xf_id,site=stage.site, project=stage.project, is_staged=True,
                                                stage=sub_stage)
                            org = stage.project.organization if stage.project else stage.site.project.organization
                            desc = "deleted form of stage {} substage {} by {}".format(stage.name, sub_stage.name,
                                                                                       self.context['request'].user.username)
                            noti = old_fsxf.logs.create(source=self.context['request'].user, type=1, title="form Deleted",
                                    organization=org, description=desc)
                            result = {}
                            result['description'] = desc
                            result['url'] = noti.get_absolute_url()
                            ChannelGroup("notify-{}".format(org.id)).send({"text": json.dumps(result)})
                            ChannelGroup("notify-0").send({"text": json.dumps(result)})

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
        fields = ('name', 'description', 'id', 'stage', 'main_stage', 'order', 'site', 'project_stage_id')


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

