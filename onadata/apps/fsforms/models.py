import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Max
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver

from onadata.apps.fieldsight.models import Site, Project
from onadata.apps.fsforms.utils import send_message
from onadata.apps.logger.models import XForm
from onadata.apps.viewer.models import ParsedInstance

SHARED_LEVEL = [(0, 'Global'), (1, 'Organization'), (2, 'Project'),]
FORM_STATUS = [(0, 'Outstanding'), (1, 'Flagged'), (2, 'Approved'), (3, 'Rejected'), ]


class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)


class FormGroup(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    shared_level = models.IntegerField(default=2, choices=SHARED_LEVEL)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="form_group")

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

    class Meta:
        db_table = 'fieldsight_forms_stage'
        verbose_name = _("FieldSight Form Stage")
        verbose_name_plural = _("FieldSight Form Stages")
        ordering = ("order",)

    def save(self, *args, **kwargs):
        if self.stage:
            self.group = self.stage.group
        self.order = Stage.get_order(self.site, self.stage)
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
        return FieldSightXF.objects.get(stage=self).xf.title

    @classmethod
    def get_order(cls, site, stage):
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

    def __unicode__(self):
        return getattr(self, "name", "")


class Days(models.Model):
    day = models.CharField(max_length=9)
    index = models.IntegerField()

    def __unicode__(self):
        return getattr(self, "day", "")


class Schedule(models.Model):
    name = models.CharField("Schedule Name", max_length=256)
    site = models.ForeignKey(Site, related_name="schedules", null=True, blank=True)
    project = models.ForeignKey(Project, related_name="schedules", null=True, blank=True)
    date_range_start = models.DateField(default=datetime.date.today)
    date_range_end = models.DateField(default=datetime.date.today)
    selected_days = models.ManyToManyField(Days,related_name='days')
    shared_level = models.IntegerField(default=2, choices=SHARED_LEVEL)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fieldsight_forms_schedule'
        verbose_name = _("Form Schedule")
        verbose_name_plural = _("Form Schedules")
        ordering = ("date_range_start",)

    def form_exists(self):
        return True if FieldSightXF.objects.filter(schedule=self).count() > 0 else False

    def form(self):
        return FieldSightXF.objects.get(schedule=self) if self.form_exists() else None

    def __unicode__(self):
        return getattr(self, "name", "")


class FieldSightXF(models.Model):
    xf = models.ForeignKey(XForm, related_name="field_sight_form")
    site = models.ForeignKey(Site, related_name="site_forms", null=True, blank=True)
    is_staged = models.BooleanField(default=False)
    is_scheduled = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now=True)
    date_modified = models.DateTimeField(auto_now=True)
    schedule = models.ForeignKey(Schedule, blank=True, null=True)
    stage = models.ForeignKey(Stage, blank=True, null=True)
    shared_level = models.IntegerField(default=2, choices=SHARED_LEVEL)
    form_status = models.IntegerField(default=0, choices=FORM_STATUS)
    # instances = models.ManyToManyField()

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

    def form_type(self):
        if self.is_scheduled: return "Scheduled"
        if self.is_staged: return "Staged"
        if not self.is_scheduled and not self.is_staged: return "Normal"

    def stage_name(self):
        if self.stage: return self.stage.name

    def schedule_name(self):
        if self.schedule: return self.schedule.name

    def clean(self):
        if self.is_staged:
            if FieldSightXF.objects.filter(xf=self.xf, site=self.site, stage=self.stage).exists():
                raise ValidationError({
                    'stage': ValidationError(_('Same Form On This Stage Found for This Site')),
                })
        if self.is_scheduled:
            if FieldSightXF.objects.filter(xf=self.xf, site=self.site, schedule=self.schedule).exists():
                raise ValidationError({
                    'schedule': ValidationError(_('Same Form On This Schedule Found for This Site')),
                })

    @staticmethod
    def get_xform_id_list(site_id):
        fs_form_list = FieldSightXF.objects.filter(site__id=site_id).order_by('xf__id').distinct('xf__id')
        return [fsform.xf.pk for fsform in fs_form_list]

    @property
    def site_name(self):
        if self.site is not None:
            return u'{}'.format(self.site.name  )



    def __unicode__(self):
        return u'{}- {}- {}'.format(self.xf, self.site, self.is_staged)

@receiver(post_save, sender=FieldSightXF)
def create_messages(sender, instance, created,  **kwargs):
    if created and instance.site is not None:
        send_message(instance)

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


