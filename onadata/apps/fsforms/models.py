from __future__ import unicode_literals
import datetime
import os

import json
import re
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Max
from django.db.models.signals import post_save, pre_delete
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from jsonfield import JSONField
from pyxform import create_survey_from_xls
from xml.dom import Node

from onadata.apps.fieldsight.models import Site, Project, Organization
from onadata.apps.fsforms.fieldsight_models import IntegerRangeField
from onadata.apps.fsforms.utils import send_message, send_message_project_form
from onadata.apps.logger.models import XForm, Instance
from onadata.apps.logger.xform_instance_parser import clean_and_parse_xml
from onadata.apps.viewer.models import ParsedInstance
from onadata.apps.fsforms.fsxform_responses import get_instances_for_field_sight_form

#To get domain to give complete url for app devs to make them easier.
from django.contrib.sites.models import Site as DjangoSite

from onadata.libs.utils.model_tools import set_uuid

SHARED_LEVEL = [(0, 'Global'), (1, 'Organization'), (2, 'Project'),]
SCHEDULED_LEVEL = [(0, 'Daily'), (1, 'Weekly'), (2, 'Monthly'),]
FORM_STATUS = [(0, 'Pending'), (1, 'Rejected'), (2, 'Flagged'), (3, 'Approved'), ]


class FormGroup(models.Model):
    name = models.CharField(max_length=256, unique=True)
    description = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="form_group")
    is_global = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization, null=True, blank=True)
    project = models.ForeignKey(Project, null=True, blank=True)
    logs = GenericRelation('eventlog.FieldSightLog')

    class Meta:
        db_table = 'fieldsight_forms_group'
        verbose_name = _("FieldSight Form Group")
        verbose_name_plural = _("FieldSight Form Groups")
        ordering = ("-date_modified",)

    def __unicode__(self):
        return getattr(self, "name", "")


class Stage(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    group = models.ForeignKey(FormGroup,related_name="stage", null=True, blank=True)
    order = IntegerRangeField(min_value=0, max_value=30,default=0)
    stage = models.ForeignKey('self', blank=True, null=True, related_name="parent")
    shared_level = models.IntegerField(default=2, choices=SHARED_LEVEL)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    site = models.ForeignKey(Site, related_name="stages", null=True, blank=True)
    project = models.ForeignKey(Project, related_name="stages", null=True, blank=True)
    ready = models.BooleanField(default=False)
    project_stage_id = models.IntegerField(default=0)
    weight = models.IntegerField(default=0)
    tags = ArrayField(models.IntegerField(), default=[])
    logs = GenericRelation('eventlog.FieldSightLog')

    class Meta:
        db_table = 'fieldsight_forms_stage'
        verbose_name = _("FieldSight Form Stage")
        verbose_name_plural = _("FieldSight Form Stages")
        ordering = ("order",)

    def save(self, *args, **kwargs):
        if self.stage:
            self.group = self.stage.group
        super(Stage, self).save(*args, **kwargs)

    def get_display_name(self):
        return "Stage" if not self.stage  else "SubStage"

    def is_main_stage(self):
        return True if not self.stage else False

    def sub_stage_count(self):
        if not self.stage:
            return Stage.objects.filter(stage=self).count()
        return 0

    def form_exists(self):
        return True if FieldSightXF.objects.filter(stage=self).count() > 0 else False

    def form_name(self):
        if not FieldSightXF.objects.filter(stage=self).count():
            return ""
        return FieldSightXF.objects.filter(stage=self)[0].xf.title

    def form(self):
        if not FieldSightXF.objects.filter(stage=self).count():
            return None
        return FieldSightXF.objects.filter(stage=self)[0]

    def active_substages(self):
        return self.parent.filter(stage_forms__isnull=False)

    def get_sub_stage_list(self):
        if not self.stage:
            return Stage.objects.filter(stage=self).values('stage_forms__id','name','stage_id')
        return []

    @property
    def xf(self):
        return FieldSightXF.objects.filter(stage=self)[0].xf.pk if self.form_exists() else None

    @property
    def form_status(self):
        status = 0
        if self.stage_forms.site_form_instances.filter(form_status=3).exists():
            status = 1
        return status

    @property
    def form_count(self):
        return self.stage_forms.site_form_instances.all().count()
    
    @staticmethod
    def site_submission_count(id, site_id):
        return Stage.objects.get(pk=id).stage_forms.project_form_instances.filter(site_id=site_id).count()
    
    
    @staticmethod
    def rejected_submission_count(id, site_id):
        return Stage.objects.get(pk=id).stage_forms.project_form_instances.filter(form_status=1, site_id=site_id).count()
    
    @staticmethod
    def flagged_submission_count(id, site_id):
        return Stage.objects.get(pk=id).stage_forms.project_form_instances.filter(form_status=2, site_id=site_id).count()
    
        
    @classmethod
    def get_order(cls, site, project, stage):
        if site:
            if not Stage.objects.filter(site=site).exists():
                return 1
            elif stage is not None:
                if not Stage.objects.filter(stage=stage).exists():
                    return 1
                else:
                    mo = Stage.objects.filter(stage=stage).aggregate(Max('order'))
                    order = mo.get('order__max', 0)
                    return order + 1
            else:
                mo = Stage.objects.filter(site=site, stage__isnull=True).aggregate(Max('order'))
                order = mo.get('order__max', 0)
                return order + 1
        else:
            if not Stage.objects.filter(project=project).exists():
                return 1
            elif stage is not None:
                if not Stage.objects.filter(stage=stage).exists():
                    return 1
                else:
                    mo = Stage.objects.filter(stage=stage).aggregate(Max('order'))
                    order = mo.get('order__max', 0)
                    return order + 1
            else:
                mo = Stage.objects.filter(project=project, stage__isnull=True).aggregate(Max('order'))
                order = mo.get('order__max', 0)
                return order + 1

    def __unicode__(self):
        return getattr(self, "name", "")


class Days(models.Model):
    day = models.CharField(max_length=9)
    index = models.IntegerField()

    def __unicode__(self):
        return getattr(self, "day", "")


class Schedule(models.Model):
    name = models.CharField("Schedule Name", max_length=256, blank=True, null=True)
    site = models.ForeignKey(Site, related_name="schedules", null=True, blank=True)
    project = models.ForeignKey(Project, related_name="schedules", null=True, blank=True)
    date_range_start = models.DateField(default=datetime.date.today)
    date_range_end = models.DateField(default=datetime.date.today)
    selected_days = models.ManyToManyField(Days, related_name='days', blank=True,)
    shared_level = models.IntegerField(default=2, choices=SHARED_LEVEL)
    schedule_level_id = models.IntegerField(default=0, choices=SCHEDULED_LEVEL)
    date_created = models.DateTimeField(auto_now_add=True)
    logs = GenericRelation('eventlog.FieldSightLog')

    class Meta:
        db_table = 'fieldsight_forms_schedule'
        verbose_name = _("Form Schedule")
        verbose_name_plural = _("Form Schedules")
        ordering = ('-date_range_start', 'date_range_end')

    def form_exists(self):
        return True if FieldSightXF.objects.filter(schedule=self).count() > 0 else False

    def form(self):
        return FieldSightXF.objects.filter(schedule=self)[0] if self.form_exists() else None

    @property
    def xf(self):
        return FieldSightXF.objects.filter(schedule=self)[0].xf.pk if self.form_exists() else None

    def __unicode__(self):
        return getattr(self, "name", "")

class DeletedXForm(models.Model):
    xf = models.OneToOneField(XForm, related_name="deleted_xform")
    date_created = models.DateTimeField(auto_now=True)

class FieldSightXF(models.Model):
    xf = models.ForeignKey(XForm, related_name="field_sight_form")
    site = models.ForeignKey(Site, related_name="site_forms", null=True, blank=True)
    project = models.ForeignKey(Project, related_name="project_forms", null=True, blank=True)
    is_staged = models.BooleanField(default=False)
    is_scheduled = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now=True)
    date_modified = models.DateTimeField(auto_now=True)
    schedule = models.OneToOneField(Schedule, blank=True, null=True, related_name="schedule_forms")
    stage = models.OneToOneField(Stage, blank=True, null=True, related_name="stage_forms")
    shared_level = models.IntegerField(default=2, choices=SHARED_LEVEL)
    form_status = models.IntegerField(default=0, choices=FORM_STATUS)
    fsform = models.ForeignKey('self', blank=True, null=True, related_name="parent")
    is_deployed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_survey = models.BooleanField(default=False)
    from_project = models.BooleanField(default=True)
    default_submission_status = models.IntegerField(default=0, choices=FORM_STATUS)
    logs = GenericRelation('eventlog.FieldSightLog')

    class Meta:
        db_table = 'fieldsight_forms_data'
        # unique_together = (("xf", "site"), ("xf", "is_staged", "stage"),("xf", "is_scheduled", "schedule"))
        verbose_name = _("XForm")
        verbose_name_plural = _("XForms")
        ordering = ("-date_created",)

    def url(self):
        return reverse(
            "download_fild_sight_form",
            kwargs={
                "site": self.site.username,
                "id_string": self.id_string
            }
        )

    def getname(self):
        return '{0} form {1}'.format(self.form_type(),
                                           self.xf.title,)
    def getresponces(self):
        return get_instances_for_field_sight_form(self.pk)

    def getlatestsubmittiondate(self):
        if self.site is not None:
            return self.site_form_instances.order_by('-pk').values('date')[:1]
        else:
            return self.project_form_instances.order_by('-pk').values('date')[:1]


    def get_absolute_url(self):
        if self.project:
            # return reverse('forms:project_html_export', kwargs={'fsxf_id': self.pk})
            return reverse('forms:setup-forms', kwargs={'is_project':1, 'pk':self.project_id})
        else:
            # return reverse('forms:formpack_html_export', kwargs={'fsxf_id': self.pk})
            return reverse('forms:setup-forms', kwargs={'is_project':0, 'pk':self.site_id})
            
    def form_type(self):
        if self.is_scheduled:
            return "scheduled"
        if self.is_staged:
            return "staged"
        if self.is_survey:
            return "survey"
        if not self.is_scheduled and not self.is_staged:
            return "general"

    def form_type_id(self):
        if self.is_scheduled and self.schedule: return self.schedule.id
        if self.is_staged and self.stage: return self.stage.id
        return None

    def stage_name(self):
        if self.stage: return self.stage.name

    def schedule_name(self):
        if self.schedule: return self.schedule.name

    def clean(self):
        if self.is_staged:
            if FieldSightXF.objects.filter(stage=self.stage).exists():
                if not FieldSightXF.objects.filter(stage=self.stage).pk == self.pk:
                    raise ValidationError({
                        'xf': ValidationError(_('Duplicate Stage Data')),
                    })
        if self.is_scheduled:
            if FieldSightXF.objects.filter(schedule=self.schedule).exists():
                if not FieldSightXF.objects.filter(schedule=self.schedule)[0].pk == self.pk:
                    raise ValidationError({
                        'xf': ValidationError(_('Duplicate Schedule Data')),
                    })
        if not self.is_scheduled and not self.is_staged:
            if self.site:
                if FieldSightXF.objects.filter(xf=self.xf, is_scheduled=False, is_staged=False,project=self.site.project).exists():
                    raise ValidationError({
                        'xf': ValidationError(_('Form Already Used in Project Level')),
                    })
            else:
                if FieldSightXF.objects.filter(xf=self.xf, is_scheduled=False, is_staged=False,
                                               site=self.site, project=self.project).exists():
                    if not FieldSightXF.objects.filter(xf=self.xf, is_scheduled=False, is_staged=False,
                                               site=self.site, project=self.project)[0].pk == self.pk:
                        raise ValidationError({
                            'xf': ValidationError(_('Duplicate General Form Data')),
                        })

    @staticmethod
    def get_xform_id_list(site_id):
        fs_form_list = FieldSightXF.objects.filter(site__id=site_id).order_by('xf__id').distinct('xf__id')
        return [fsform.xf.pk for fsform in fs_form_list]

    @property
    def site_name(self):
        if self.site is not None:
            return u'{}'.format(self.site.name)\

    @property
    def site_or_project_display(self):
        if self.site is not None:
            return u'{}'.format(self.site.name)
        return u'{}'.format(self.project.name)

    @property
    def project_info(self):
        if self.fsform:
            self.fsform.pk
        return None

    def __unicode__(self): 
        return u'{}- {}- {}'.format(self.xf, self.site, self.is_staged)

@receiver(post_save, sender=FieldSightXF)
def create_messages(sender, instance, created,  **kwargs):
    if instance.project is not None and created and not instance.is_staged:
        send_message_project_form(instance)
    elif created and instance.site is not None and not instance.is_staged:
        send_message(instance)


@receiver(pre_delete, sender=FieldSightXF)
def send_delete_message(sender, instance, using, **kwargs):
    if instance.project is not None:
        pass
    elif instance.is_staged:
        pass
    else:
        fxf = instance
        send_message(fxf)

post_save.connect(create_messages, sender=FieldSightXF)


class FieldSightParsedInstance(ParsedInstance):
    _update_fs_data = None

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self._update_fs_data = kwargs.pop('update_fs_data', {})
        super(FieldSightParsedInstance, self).save(*args, **kwargs)

    def to_dict_for_mongo(self):
        mongo_dict = super(FieldSightParsedInstance, self).to_dict_for_mongo()
        mongo_dict.update(self._update_fs_data)
        return mongo_dict

    @staticmethod
    def get_or_create(instance, update_data=None):
        if update_data is None:
            update_data = {}
        created = False
        try:
            fspi = FieldSightParsedInstance.objects.get(instance__pk=instance.pk)
            fspi.save(update_fs_data=update_data, async=False)
        except FieldSightParsedInstance.DoesNotExist:
            created = True
            fspi = FieldSightParsedInstance(instance=instance)
            fspi.save(update_fs_data=update_data, async=False)
        return fspi, created




class FInstanceManager(models.Manager):
    def get_queryset(self):
        return super(FInstanceManager, self).get_queryset().filter(is_deleted=False)


class FInstanceDeletedManager(models.Manager):
    def get_queryset(self):
        return super(FInstanceDeletedManager, self).get_queryset().filter(is_deleted=True)


class FInstance(models.Model):
    instance = models.OneToOneField(Instance, related_name='fieldsight_instance')
    site = models.ForeignKey(Site, null=True, related_name='site_instances')
    project = models.ForeignKey(Project, null=True, related_name='project_instances')
    site_fxf = models.ForeignKey(FieldSightXF, null=True, related_name='site_form_instances', on_delete=models.SET_NULL)
    project_fxf = models.ForeignKey(FieldSightXF, null=True, related_name='project_form_instances')
    form_status = models.IntegerField(null=True, blank=True, choices=FORM_STATUS)
    date = models.DateTimeField(auto_now=True)
    submitted_by = models.ForeignKey(User, related_name="supervisor")
    is_deleted = models.BooleanField(default=False)
    version = models.CharField(max_length=255, default=u'')
    objects = FInstanceManager()
    deleted_objects = FInstanceDeletedManager()
    logs = GenericRelation('eventlog.FieldSightLog')

    @property
    def get_version(self):
        import re
        p = re.compile('<__version__>(.*)</__version__>')
        m = p.search(self.instance.xml)
        if m:
            return m.group(1)
        return None

    def set_version(self):
        import re
        p = re.compile('<__version__>(.*)</__version__>')
        m = p.search(self.instance.xml)
        if m:
            self.version = m.group(1)
            self.save()

    def save(self, *args, **kwargs):
        self.version = self.get_version
        if self.form_status is None:
            if self.site_fxf:
                self.form_status = self.site_fxf.default_submission_status
            else:
                self.form_status = self.project_fxf.default_submission_status                
        super(FInstance, self).save(*args, **kwargs)  # Call the "real" save() method.
        
    @property
    def fsxfid(self):
        if self.project_fxf:
            return self.project_fxf.id
        else:
            return self.site_fxf.id\

    @property
    def fsxf(self):
        if self.project_fxf:
            return self.project_fxf
        else:
            return self.site_fxf

    def get_absolute_url(self):

        if self.site_fxf:
            fxf_id = self.site_fxf_id
        else:
            fxf_id = self.project_fxf_id
            
        return "/forms/forms/" + str(fxf_id) + "#/" + str(self.instance.id)

 
    def get_abr_form_status(self):
        return dict(FORM_STATUS)[self.form_status]    


    def getname(self):
        if self.site_fxf is None:
        
            return '{0} form {1}'.format(self.project_fxf.form_type(), self.project_fxf.xf.title,)
        
        return '{0} form {1}'.format(self.site_fxf.form_type(),
                                           self.site_fxf.xf.title,)
    def __unicode__(self):
        if self.site_fxf is None:
            return u"%s" % str(self.submitted_by) + "---" + self.project_fxf.xf.title
        return u"%s" % str(self.submitted_by) + "---" + self.site_fxf.xf.title

    def instance_json(self):
        return json.dumps(self.instance.json)

    def get_responces(self):
        data=[]
        json_answer = self.instance.json
        json_question = json.loads(self.instance.xform.json)
        base_url = DjangoSite.objects.get_current().domain
        media_folder = self.instance.xform.user.username
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
                        if r_question+"/"+question in gnr_answer:
                            if first_children['type'] == 'note':
                                answer= ''
                            elif first_children['type'] == 'photo' or first_children['type'] == 'audio' or first_children['type'] == 'video':
                                answer = 'http://'+base_url+'/attachment/medium?media_file=/'+ media_folder +'attachments/'+gnr_answer[r_question+"/"+question]
                            else:
                                answer = gnr_answer[r_question+"/"+question]
                                
                        if 'label' in first_children:
                            question = first_children['label']
                        row={'type':question_type, 'question':question, 'answer':answer}
                        data.append(row)
            else:
                for first_children in r_object['children']:
                        question_type = first_children['type']
                        question = first_children['name']
                        answer = ''
                        if 'label' in first_children:
                            question = first_children['label']
                        row={'type':question_type, 'question':question, 'answer':answer}
                        data.append(row)


        def parse_group(prev_groupname, g_object):
            g_question = prev_groupname+g_object['name']
            for first_children in g_object['children']:
                question = first_children['name']
                question_type = first_children['type']
                if question_type == 'group':
                    parse_group(g_question+"/",first_children)
                    continue
                answer = ''
                if g_question+"/"+question in json_answer:
                    if question_type == 'note':
                        answer= '' 
                    elif question_type == 'photo' or question_type == 'audio' or question_type == 'video':
                        answer = 'http://'+base_url+'/attachment/medium?media_file=/'+ media_folder +'attachments/'+json_answer[g_question+"/"+question]
                    else:
                        answer = json_answer[g_question+"/"+question]

                if 'label' in first_children:
                    question = first_children['label']
                row={'type':question_type, 'question':question, 'answer':answer}
                data.append(row)
                

        def parse_individual_questions(parent_object):
            for first_children in parent_object:
                if first_children['type'] == "repeat":
                    parse_repeat(first_children)
                elif first_children['type'] == 'group':
                    parse_group("",first_children)
                else:
                    question = first_children['name']
                    question_type = first_children['type']
                    answer= ''
                    if question in json_answer:
                        if first_children['type'] == 'note':
                            answer= '' 
                        elif first_children['type'] == 'photo' or first_children['type'] == 'audio' or first_children['type'] == 'video':
                            answer = 'http://'+base_url+'/attachment/medium?media_file=/'+ media_folder +'attachments/'+json_answer[question]
                        else:
                            answer = json_answer[question]
                    if 'label' in first_children:
                        question = first_children['label']
                    row={"type":question_type, "question":question, "answer":answer}
                    data.append(row)

            submitted_by={'type':'submitted_by','question':'Submitted by', 'answer':json_answer['_submitted_by']}
            submittion_time={'type':'submittion_time','question':'Submittion Time', 'answer':json_answer['_submission_time']}
            data.append(submitted_by)
            data.append(submittion_time)
        parse_individual_questions(json_question['children'])
        return data

class InstanceStatusChanged(models.Model):
    finstance = models.ForeignKey(FInstance, related_name="comments")
    message = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
    old_status = models.IntegerField(default=0, choices=FORM_STATUS)
    new_status = models.IntegerField(default=0, choices=FORM_STATUS)
    user = models.ForeignKey(User, related_name="submission_comments")
    logs = GenericRelation('eventlog.FieldSightLog')

    class Meta:
        ordering = ['-date']

    def get_absolute_url(self):
        return reverse('forms:alter-status-detail', kwargs={'pk': self.pk})

    def getname(self):
        return '{0} form {1}'.format(self.finstance.site_fxf.form_type(), self.finstance.site_fxf.xf.title)

class InstanceImages(models.Model):
    instance_status = models.ForeignKey(InstanceStatusChanged, related_name="images")
    image = models.ImageField(upload_to="submission-feedback-images",
                              verbose_name='Status Changed Images',)



class FieldSightFormLibrary(models.Model):
    xf = models.ForeignKey(XForm)
    is_global = models.BooleanField(default=False)
    shared_date = models.DateTimeField(auto_now=True)
    organization = models.ForeignKey(Organization, null=True, blank=True)
    project = models.ForeignKey(Project, null=True, blank=True)
    logs = GenericRelation('eventlog.FieldSightLog')

    class Meta:
        verbose_name = _("Library")
        verbose_name_plural = _("Library")
        ordering = ("-shared_date",)


class EducationMaterial(models.Model):
    is_pdf = models.BooleanField(default=False)
    pdf = models.FileField(upload_to="education-material-pdf", null=True, blank=True)
    title = models.CharField(max_length=31, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    stage = models.OneToOneField(Stage, related_name="em", null=True, blank=True)
    fsxf = models.OneToOneField(FieldSightXF, related_name="em", null=True, blank=True)


class EducationalImages(models.Model):
    educational_material = models.ForeignKey(EducationMaterial, related_name="em_images")
    image = models.ImageField(upload_to="education-material-images",
                              verbose_name='Education Images',)

# @receiver(post_save, sender=Site)
# def copy_stages_from_project(sender, **kwargs):
#     site = kwargs.get('instance')
#     created = kwargs.get('created')
#     if created:
#         project = site.project
#         project_main_stages = project.stages.filter(stage__isnull=True)
#         for pms in project_main_stages:
#             project_sub_stages = Stage.objects.filter(stage__id=pms.pk, stage_forms__is_deleted=False, stage_forms__is_deployed=True)
#             if not project_sub_stages:
#                 continue
#             site_main_stage = Stage(name=pms.name, order=pms.order, site=site, description=pms.description,
#                                     project_stage_id=pms.id, weight=pms.weight)
#             site_main_stage.save()
#             for pss in project_sub_stages:
#                 if pss.tags and site.type:
#                     if site.type.id not in pss.tags:
#                         continue
#                 site_sub_stage = Stage(name=pss.name, order=pss.order, site=site,
#                                description=pss.description, stage=site_main_stage, project_stage_id=pss.id, weight=pss.weight)
#                 site_sub_stage.save()
#                 if FieldSightXF.objects.filter(stage=pss).exists():
#                     fsxf = pss.stage_forms
#                     site_form = FieldSightXF(is_staged=True, default_submission_status=fsxf.default_submission_status, xf=fsxf.xf, site=site,fsform=fsxf, stage=site_sub_stage, is_deployed=True)
#                     site_form.save()
#         general_forms = project.project_forms.filter(is_staged=False, is_scheduled=False, is_deployed=True, is_deleted=False)
#         for general_form in general_forms:
#             FieldSightXF.objects.create(is_staged=False, default_submission_status=general_form.default_submission_status, is_scheduled=False, is_deployed=True, site=site,
#                                         xf=general_form.xf, fsform=general_form)
#
#         schedule_forms = project.project_forms.filter(is_scheduled=True, is_deployed=True, is_deleted=False)
#         for schedule_form in schedule_forms:
#             schedule = schedule_form.schedule
#             selected_days = tuple(schedule.selected_days.all())
#             s = Schedule.objects.create(name=schedule.name, site=site, date_range_start=schedule.date_range_start,
#                                         date_range_end=schedule.date_range_end)
#             s.selected_days.add(*selected_days)
#             s.save()
#             FieldSightXF.objects.create(is_scheduled=True, default_submission_status=schedule_form.default_submission_status, xf=schedule_form.xf, site=site, fsform=schedule_form,
#                                              schedule=s, is_deployed=True)


class DeployEvent(models.Model):
    form_changed = models.BooleanField(default=True)
    data = JSONField(default={})
    date = models.DateTimeField(auto_now=True)
    site = models.ForeignKey(Site, related_name="deploy_data", null=True)
    project = models.ForeignKey(Project, related_name="deploy_data", null=True)

def upload_to(instance, filename):
    return os.path.join(
        'versions', str(instance.pk),
        'xls',
        os.path.split(filename)[1])


class XformHistory(models.Model):
        class Meta:
            unique_together = ('xform', 'version')

        def _set_uuid_in_xml(self, file_name=None):
            """
            Add bind to automatically set UUID node in XML.
            """
            if not file_name:
                file_name = self.file_name()
            file_name, file_ext = os.path.splitext(file_name)

            doc = clean_and_parse_xml(self.xml)
            model_nodes = doc.getElementsByTagName("model")
            if len(model_nodes) != 1:
                raise Exception(u"xml contains multiple model nodes")

            model_node = model_nodes[0]
            instance_nodes = [node for node in model_node.childNodes if
                              node.nodeType == Node.ELEMENT_NODE and
                              node.tagName.lower() == "instance" and
                              not node.hasAttribute("id")]

            if len(instance_nodes) != 1:
                raise Exception(u"Multiple instance nodes without the id "
                                u"attribute, can't tell which is the main one")

            instance_node = instance_nodes[0]

            # get the first child whose id attribute matches our id_string
            survey_nodes = [node for node in instance_node.childNodes
                            if node.nodeType == Node.ELEMENT_NODE and
                            (node.tagName == file_name or
                             node.attributes.get('id'))]

            if len(survey_nodes) != 1:
                raise Exception(
                    u"Multiple survey nodes with the id '%s'" % self.id_string)

            survey_node = survey_nodes[0]
            formhub_nodes = [n for n in survey_node.childNodes
                             if n.nodeType == Node.ELEMENT_NODE and
                             n.tagName == "formhub"]

            if len(formhub_nodes) > 1:
                raise Exception(
                    u"Multiple formhub nodes within main instance node")
            elif len(formhub_nodes) == 1:
                formhub_node = formhub_nodes[0]
            else:
                formhub_node = survey_node.insertBefore(
                    doc.createElement("formhub"), survey_node.firstChild)

            uuid_nodes = [node for node in formhub_node.childNodes if
                          node.nodeType == Node.ELEMENT_NODE and
                          node.tagName == "uuid"]

            if len(uuid_nodes) == 0:
                formhub_node.appendChild(doc.createElement("uuid"))
            if len(formhub_nodes) == 0:
                # append the calculate bind node
                calculate_node = doc.createElement("bind")
                calculate_node.setAttribute(
                    "nodeset", "/%s/formhub/uuid" % file_name)
                calculate_node.setAttribute("type", "string")
                calculate_node.setAttribute("calculate", "'%s'" % self.uuid)
                model_node.appendChild(calculate_node)

            self.xml = doc.toprettyxml(indent="  ", encoding='utf-8')
            # hack
            # http://ronrothman.com/public/leftbraned/xml-dom-minidom-toprettyxml-\
            # and-silly-whitespace/
            text_re = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)
            output_re = re.compile('\n.*(<output.*>)\n(  )*')
            prettyXml = text_re.sub('>\g<1></', self.xml)
            inlineOutput = output_re.sub('\g<1>', prettyXml)
            inlineOutput = re.compile('<label>\s*\n*\s*\n*\s*</label>').sub(
                '<label></label>', inlineOutput)
            self.xml = inlineOutput

        xform = models.ForeignKey(XForm, related_name="fshistory")
        date = models.DateTimeField(auto_now=True)
        xls = models.FileField(upload_to=upload_to, null=True)
        json = models.TextField(default=u'')
        description = models.TextField(default=u'', null=True)
        xml = models.TextField()
        id_string = models.CharField(editable=False, max_length=255)
        title = models.CharField(editable=False, max_length=255)
        uuid = models.CharField(max_length=32, default=u'')
        version = models.CharField(max_length=255, default=u'')

        @property
        def get_version(self):
            import re
            p = re.compile('version="(.*)">')
            m = p.search(self.xml)
            if m:
                return m.group(1)
            return None

        def save(self, *args, **kwargs):
            if self.xls and not self.xml:
                survey = create_survey_from_xls(self.xls)
                self.json = survey.to_json()
                self.xml = survey.to_xml()
                self._mark_start_time_boolean()
                set_uuid(self)
                self._set_uuid_in_xml()
            if not self.version:
                self.version = self.get_version
            super(XformHistory, self).save(*args, **kwargs)

        def file_name(self):
            return os.path.split(self.xls.name)[-1]

        def _mark_start_time_boolean(self):
            starttime_substring = 'jr:preloadParams="start"'
            if self.xml.find(starttime_substring) != -1:
                self.has_start_time = True
            else:
                self.has_start_time = False


class SubmissionOfflineSite(models.Model):
    offline_site_id = models.CharField(max_length=20)
    temporary_site = models.ForeignKey(Site, related_name="offline_submissions")
    instance = models.OneToOneField(FInstance, blank=True, null=True, related_name="offline_submission")
    fieldsight_form = models.ForeignKey(FieldSightXF, related_name="offline_submissiob" , null=True, blank=True)

    def __unicode__(self):
        if self.instance:
            return u"%s ---------------%s" % (str(self.instance.id) ,self.offline_site_id)
        return u"%s" % str(self.offline_site_id)
