import json

from rest_framework import serializers

from onadata.apps.fieldsight.models import Project, Site
from onadata.apps.fsforms.models import Stage, FieldSightXF, EducationalImages, EducationMaterial, DeployEvent, \
    FInstance
from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import EMSerializer
from onadata.apps.fsforms.serializers.InstanceStatusChangedSerializer import FSXFSerializer
from onadata.apps.logger.models import XForm, Instance

from django.contrib.sites.models import Site as DjangoSite
BASEURL = DjangoSite.objects.get_current().domain



class StageSerializer(serializers.ModelSerializer):
    sub_stage_weight = serializers.SerializerMethodField()

    class Meta:
        model = Stage
        fields = ('name', 'description', 'id', 'order', 'tags',
                  'weight' ,'sub_stage_weight', 'stage',
                  'project_stage_id', 'site')
        read_only_fields = ('stage' ,'project_stage_id','site')

    def get_sub_stage_weight(self, obj):
        if hasattr(obj, 'sub_stage_weight'):
            return obj.sub_stage_weight if obj.sub_stage_weight else 0
        return 0

    def create(self, validated_data):
        pk = self.context['kwargs'].get('pk')
        is_project = self.context['kwargs'].get('is_project')
        stage = super(StageSerializer, self).create(validated_data)
        if is_project == "1":
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
        fields = ('name', 'description', 'id', 'order', 'tags', 'weight')


class SubStageDetailSerializer(serializers.ModelSerializer):
    stage_forms = FSXFSerializer(read_only=True)
    em = EMSerializer(read_only=True)
    responses_count = serializers.SerializerMethodField()
    has_stage = serializers.SerializerMethodField()
    has_em = serializers.SerializerMethodField()
    is_deployed = serializers.SerializerMethodField()
    default_submission_status = serializers.SerializerMethodField()

    def get_responses_count(self, obj):
        try:
            request = self.context.get('request', False)
            params = {}
            if request:
                params = request.query_params
            site_id = False
            if params.get("is_project", False):
                if params.get("is_project") == "0":
                    site_id = params.get("pk", False)

            fsxf = FieldSightXF.objects.get(stage=obj)

            if fsxf.site is None:
                if site_id:
                    return fsxf.project_form_instances.filter(site=site_id).count()
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

    def get_default_submission_status(self, obj):
        try:
            return obj.stage_forms.default_submission_status
        except:
            return 0
    class Meta:
        model = Stage
        fields = ('weight', 'name', 'description', 'id', 'order', 'date_created', 'em', 'responses_count',
                  'stage_forms', 'has_stage', 'has_em', 'tags', 'is_deployed', 'default_submission_status')

    def create(self, validated_data):
        stage_id = self.context['kwargs'].get('stage_id')
        default_submission_status = self.context['request'].data.get('default_submission_status', 0)
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
                                                      project=main_stage.project, is_staged=True, stage=stage, default_submission_status=default_submission_status)
        stage.stage = main_stage
        stage.site = main_stage.site
        stage.project = main_stage.project
        stage.save()
        # tags
        return stage

    def update(self,instance, validated_data):
        xf = self.context['request'].data.get('xf', {})
        default_submission_status = self.context['request'].data.get('default_submission_status', 0)
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
                    old_form.default_submission_status = default_submission_status
                    old_form.save()
                else:
                    old_form.is_deleted = True
                    old_form.stage = None
                    old_form.save()
                    FieldSightXF.objects.create(xf=xform, site=stage.stage.site,
                                                  project=stage.stage.project, is_staged=True, stage=stage, default_submission_status = default_submission_status)
            except:
                if xform:
                    FieldSightXF.objects.create(xf=xform, site=stage.stage.site,
                                                      project=stage.stage.project, is_staged=True, stage=stage, default_submission_status = default_submission_status)
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


class DeploySerializer(serializers.ModelSerializer):
    clean_data = serializers.SerializerMethodField()

    class Meta:
        model = DeployEvent
        exclude = ('data',)

    def get_clean_data(self, obj):
        return dict(obj.data)

class InstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instance
        fields = ('json',)


class FinstanceSerializer(serializers.ModelSerializer):
    # instance = InstanceSerializer()
    submission_data = serializers.SerializerMethodField()
    submitted_by = serializers.SerializerMethodField()
    form_type = serializers.SerializerMethodField()

    class Meta:
        model = FInstance
        fields = ('submission_data', 'site', 'project', 'site_fxf', 'project_fxf', 'date', 'submitted_by', 'form_type')

    def get_submitted_by(self, obj):
        return obj.submitted_by.username

    def get_form_type(self, obj):
        return {'is_staged': obj.site_fxf.is_staged, 'is_scheduled': obj.site_fxf.is_scheduled, 'is_survey': obj.site_fxf.is_survey, }

    def get_submission_data(self, obj):
        data = []
        json_answer = obj.instance.json
        json_question = json.loads(obj.site_fxf.xf.json)
        base_url = BASEURL
        media_folder = obj.site_fxf.xf.user.username

        def parse_repeat(r_object):
            r_question = r_object['name']
            data.append(r_question)

            if r_question in json_answer:
                for gnr_answer in json_answer[r_question]:
                    for first_children in r_object['children']:
                        question_type = first_children['type']
                        question = first_children['name']
                        group_answer = json_answer[r_question]
                        answer = ''
                        if r_question + "/" + question in gnr_answer:
                            if first_children['type'] == 'note':
                                answer = ''
                            elif first_children['type'] == 'photo' or first_children['type'] == 'audio' or \
                                    first_children['type'] == 'video':
                                answer = 'http://' + base_url + '/attachment/medium?media_file=' + media_folder + '/attachments/' + gnr_answer[
                                    r_question + "/" + question]
                            else:
                                answer = gnr_answer[r_question + "/" + question]

                        if 'label' in first_children:
                            question = first_children['label']
                        row = {'type': question_type, 'question': question, 'answer': answer}
                        data.append(row)
            else:
                for first_children in r_object['children']:
                    question_type = first_children['type']
                    question = first_children['name']
                    answer = ''
                    if 'label' in first_children:
                        question = first_children['label']
                    row = {'type': question_type, 'question': question, 'answer': answer}
                    data.append(row)

        def parse_group(prev_groupname, g_object):
            g_question = prev_groupname + g_object['name']
            for first_children in g_object['children']:
                question = first_children['name']
                question_type = first_children['type']
                if question_type == 'group':
                    parse_group(g_question + "/", first_children)
                    continue
                answer = ''
                if g_question + "/" + question in json_answer:
                    if question_type == 'note':
                        answer = ''
                    elif question_type == 'photo' or question_type == 'audio' or question_type == 'video':
                        answer = 'http://' + base_url + '/attachment/medium?media_file=' + media_folder + '/attachments/' + json_answer[
                            g_question + "/" + question]
                    else:
                        answer = json_answer[g_question + "/" + question]

                if 'label' in first_children:
                    question = first_children['label']
                row = {'type': question_type, 'question': question, 'answer': answer}
                data.append(row)

        def parse_individual_questions(parent_object):
            for first_children in parent_object:
                if first_children['type'] == "repeat":
                    parse_repeat(first_children)
                elif first_children['type'] == 'group':
                    parse_group("", first_children)
                else:
                    question = first_children['name']
                    question_type = first_children['type']
                    answer = ''
                    if question in json_answer:
                        if first_children['type'] == 'note':
                            answer = ''
                        elif first_children['type'] == 'photo' or first_children['type'] == 'audio' or first_children[
                            'type'] == 'video':
                            answer = 'http://' + base_url + '/attachment/medium?media_file=' + media_folder + '/attachments/' + json_answer[
                                question]
                        else:
                            answer = json_answer[question]
                    if 'label' in first_children:
                        question = first_children['label']
                    row = {"type": question_type, "question": question, "answer": answer}
                    data.append(row)

            submitted_by = {'type': 'submitted_by', 'question': 'Submitted by', 'answer': json_answer['_submitted_by']}
            submittion_time = {'type': 'submittion_time', 'question': 'Submittion Time',
                               'answer': json_answer['_submission_time']}
            data.append(submitted_by)
            data.append(submittion_time)

        parse_individual_questions(json_question['children'])
        return data

