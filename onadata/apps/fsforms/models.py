import datetime
import json
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Max
from django.db.models.signals import post_save, pre_delete
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver

from onadata.apps.fieldsight.models import Site, Project, Organization
from onadata.apps.fsforms.fieldsight_models import IntegerRangeField
from onadata.apps.fsforms.utils import send_message
from onadata.apps.logger.models import XForm, Instance
from onadata.apps.viewer.models import ParsedInstance
from onadata.apps.fsforms.fsxform_responses import get_instances_for_field_sight_form

SHARED_LEVEL = [(0, 'Global'), (1, 'Organization'), (2, 'Project'),]
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
            return False
        return FieldSightXF.objects.filter(stage=self)

    def active_substages(self):
        return self.parent.filter(stage_forms__isnull=False)

    @property
    def xf(self):
        return FieldSightXF.objects.filter(stage=self)[0].xf.pk if self.form_exists() else None

    @property
    def form_status(self):
        status = 0
        if self.stage_forms.site_form_instances.filter(form_status=3).exists():
            status = 1
        return status


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
    selected_days = models.ManyToManyField(Days,related_name='days',blank=True,)
    shared_level = models.IntegerField(default=2, choices=SHARED_LEVEL)
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

    def get_absolute_url(self):
        if self.project:
            # return reverse('forms:project_html_export', kwargs={'fsxf_id': self.pk})
            return reverse('forms:setup-forms', kwargs={'is_project':1, 'pk':self.project_id})
        else:
            # return reverse('forms:formpack_html_export', kwargs={'fsxf_id': self.pk})
            return reverse('forms:setup-forms', kwargs={'is_project':0, 'pk':self.site_id})
            
    def form_type(self):
        if self.is_scheduled: return "Scheduled"
        if self.is_staged: return "Staged"
        if self.is_survey: return "Surveyed"
        if not self.is_scheduled and not self.is_staged: return "General"

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
            return u'{}'.format(self.site.name)
    @property
    def project_info(self):
        if self.fsform:
            self.fsform.pk
        return None

    def __unicode__(self): 
        return u'{}- {}- {}'.format(self.xf, self.site, self.is_staged)

@receiver(post_save, sender=FieldSightXF)
def create_messages(sender, instance, created,  **kwargs):
    if instance.project is not None:
        pass
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
        except FieldSightParsedInstance.DoesNotExist:
            created = True
            fspi = FieldSightParsedInstance(instance=instance)
            fspi.save(update_fs_data=update_data, async=False)
        return fspi, created


class FInstance(models.Model):
    instance = models.OneToOneField(Instance, related_name='fieldsight_instance')
    site = models.ForeignKey(Site, null=True, related_name='site_instances')
    project = models.ForeignKey(Project, null=True, related_name='project_instances')
    site_fxf = models.ForeignKey(FieldSightXF, null=True, related_name='site_form_instances')
    project_fxf = models.ForeignKey(FieldSightXF, null=True, related_name='project_form_instances')
    form_status = models.IntegerField(default=0, choices=FORM_STATUS)
    date = models.DateTimeField(auto_now=True)
    submitted_by = models.ForeignKey(User, related_name="supervisor")
    logs = GenericRelation('eventlog.FieldSightLog')

    @property
    def fsxfid(self):
        if self.project_fxf:
            return self.project_fxf.id
        else:
            return self.site_fxf.id

    def get_absolute_url(self):
        return reverse('forms:instance', kwargs={'fsxf_id': self.site_fxf.pk})

    def getname(self):
        return '{0} form {1}'.format(self.site_fxf.form_type(),
                                           self.site_fxf.xf.title,)
    def __unicode__(self):
        return u"%s" % str(self.submitted_by) + "---" + self.site_fxf.xf.title

    def instance_json(self):
        return json.dumps(self.instance.json)

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

@receiver(post_save, sender=Site)
def copy_stages_from_project(sender, **kwargs):
    site = kwargs.get('instance')
    created = kwargs.get('created')
    if created:
        project = site.project
        project_main_stages = project.stages.filter(stage__isnull=True)
        for pms  in project_main_stages:
            project_sub_stages = Stage.objects.filter(stage__id=pms.pk, stage_forms__is_deleted=False)
            site_main_stage = Stage(name=pms.name, order=pms.order, site=site, description=pms.description, project_stage_id=pms.id)
            site_main_stage.save()
            for pss in project_sub_stages:
                site_sub_stage = Stage(name=pss.name, order=pss.order, site=site,
                               description=pss.description, stage=site_main_stage, project_stage_id=pss.id)
                site_sub_stage.save()
                if FieldSightXF.objects.filter(stage=pss).exists():
                    fsxf = pss.stage_forms
                    site_form = FieldSightXF(is_staged=True, xf=fsxf.xf, site=site,fsform=fsxf, stage=site_sub_stage, is_deployed=True)
                    site_form.save()
        general_forms = project.project_forms.filter(is_staged=False, is_scheduled=False, is_deployed=True, is_deleted=False)
        for general_form in general_forms:
            FieldSightXF.objects.create(is_staged=False, is_scheduled=False, is_deployed=True, site=site,
                                        xf=general_form.xf, fsform=general_form)

        schedule_forms = project.project_forms.filter(is_scheduled=True, is_deployed=True, is_deleted=False)
        for schedule_form in schedule_forms:
            schedule = schedule_form.schedule
            selected_days = tuple(schedule.selected_days.all())
            s = Schedule.objects.create(name=schedule.name, site=site, date_range_start=schedule.date_range_start,
                                        date_range_end=schedule.date_range_end)
            s.selected_days.add(*selected_days)
            s.save()
            FieldSightXF.objects.create(is_scheduled=True, xf=schedule_form.xf, site=site, fsform=schedule_form,
                                             schedule=s, is_deployed=True)