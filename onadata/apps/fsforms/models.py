import datetime
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
    logs = GenericRelation('eventlog.FieldSightLog')

    class Meta:
        db_table = 'fieldsight_forms_stage'
        verbose_name = _("FieldSight Form Stage")
        verbose_name_plural = _("FieldSight Form Stages")
        ordering = ("order",)

    def save(self, *args, **kwargs):
        if self.stage:
            self.group = self.stage.group
        # if not self.pk:
        #     self.order = Stage.get_order(self.site, self.project,self.stage)
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



class EducationMaterial(models.Model):
    is_pdf = models.BooleanField(default=False)
    pdf = models.FileField(upload_to="education-material-pdf", null=True, blank=True)
    title = models.CharField(max_length=31, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    stage = models.OneToOneField(Stage, related_name="em")


class EducationalImages(models.Model):
    educational_material = models.ForeignKey(EducationMaterial, related_name="em_images")
    image = models.ImageField(upload_to="education-material-images",
                              verbose_name='Education Images',)




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

    def get_absolute_url(self):
        if self.project:
            return reverse('forms:project_html_export', kwargs={'fsxf_id': self.pk})
        else:
            return reverse('forms:formpack_html_export', kwargs={'fsxf_id': self.pk})

    def form_type(self):
        if self.is_scheduled: return "Scheduled"
        if self.is_staged: return "Staged"
        if not self.is_scheduled and not self.is_staged: return "General"

    def form_type_id(self):
        if self.is_scheduled: return self.schedule.id
        if self.is_staged: return self.stage.id
        if not self.is_scheduled and not self.is_staged: return None

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


class InstanceStatusChanged(models.Model):
    finstance = models.ForeignKey(FInstance, related_name="comments")
    message = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
    old_status = models.IntegerField(default=0, choices=FORM_STATUS)
    new_status = models.IntegerField(default=0, choices=FORM_STATUS)
    user = models.ForeignKey(User, related_name="submission_comments")
    logs = GenericRelation('eventlog.FieldSightLog')


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