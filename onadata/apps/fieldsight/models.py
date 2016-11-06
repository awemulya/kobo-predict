from datetime import datetime
from django.contrib.auth.models import Group
from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models import GeoManager
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from .static_lists import COUNTRIES


class ExtraUserDetail(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='extra_details')
    data = JSONField(default={})

    def __unicode__(self):
        return '{}\'s data: {}'.format(self.user.__unicode__(), repr(self.data))


def create_extra_user_details(sender, instance, created, **kwargs):
    if created:
        ExtraUserDetail.objects.get_or_create(user=instance)


post_save.connect(create_extra_user_details, sender=settings.AUTH_USER_MODEL)


class OrganizationType(models.Model):
    name = models.CharField("Organization Type", max_length=256)

    def __unicode__(self):
        return u'{}'.format(self.name)


class ProjectType(models.Model):
    name = models.CharField("Project Type", max_length=256)

    def __unicode__(self):
        return u'{}'.format(self.name)


class Organization(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=3, choices=COUNTRIES, default=u'NPL')
    type = models.ForeignKey(OrganizationType, verbose_name='Type of Organization')
    public_desc = models.TextField("Public Description", blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    location = PointField(geography=True, srid=4326, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    additional_desc = models.TextField("Additional Description", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return u'{}'.format(self.name)

    objects = GeoManager()

    @property
    def latitude(self):
        if self.point:
            return self.point.y

    @property
    def longitude(self):
        if self.point:
            return self.point.x

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('organization-detail', kwargs={'pk': self.pk})

    @property
    def get_staffs(self):
        staffs = list(self.organization_roles.filter(group__name="Organization Admin"))
        if staffs:
            return [str(role.user.username) for role in staffs]
        return ""\

    @property
    def get_staffs_id(self):
        staffs = list(self.organization_roles.filter(group__name="Organization Admin"))
        if staffs:
            return [role.user.id for role in staffs]
        return []


class Project(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(ProjectType, verbose_name='Type of Project')
    donor = models.CharField(max_length=256, blank=True, null=True)
    public_desc = models.TextField("Public Description", blank=True, null=True)
    additional_desc = models.TextField("Additional Description", blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    location = PointField(geography=True, srid=4326, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    organization = models.ForeignKey(Organization, related_name='projects')
    is_active = models.BooleanField(default=True)

    objects = GeoManager()

    @property
    def latitude(self):
        if self.point:
            return self.point.y

    @property
    def longitude(self):
        if self.point:
            return self.point.x

    def __str__(self):
        return self.name

    @property
    def get_staffs(self):
        staffs = list(self.project_roles.filter(group__name="Project Manager"))
        if staffs:
            return [str(role.user.username) for role in staffs]
        return ""\

    @property
    def get_staffs_id(self):
        staffs = list(self.project_roles.filter(group__name="Project Manager"))
        if staffs:
            return [role.user.id for role in staffs]
        return []


class Site(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(ProjectType, verbose_name='Type of Site')
    public_desc = models.TextField("Public Description", blank=True, null=True)
    additional_desc = models.TextField("Additional Description", blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    location = PointField(geography=True, srid=4326, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    project = models.ForeignKey(Project, related_name='sites')
    is_active = models.BooleanField(default=True)

    objects = GeoManager()

    @property
    def latitude(self):
        if self.point:
            return self.point.y

    @property
    def longitude(self):
        if self.point:
            return self.point.x

    def __str__(self):
        return self.name

    @property
    def get_central_eng(self):
        staffs = list(self.site_roles.filter(group__name="Central Engineer"))
        if staffs:
            return [str(role.user.username) for role in staffs]
        return ""\

    @property
    def get_central_eng_id(self):
        staffs = list(self.site_roles.filter(group__name="Central Engineer"))
        if staffs:
            return [role.user.id for role in staffs]
        return []

    @property
    def get_supervisors(self):
        staffs = list(self.site_roles.filter(group__name="Site Supervisor"))
        if staffs:
            return [str(role.user.username) for role in staffs]
        return ""\

    @property
    def get_supervisor_id(self):
        staffs = list(self.site_roles.filter(group__name="Site Supervisor"))
        if staffs:
            return [role.user.id for role in staffs]
        return []


class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_roles")
    group = models.ForeignKey(Group)
    started_at = models.DateTimeField(default=datetime.now)
    ended_at = models.DateTimeField(blank=True, null=True)
    site = models.ForeignKey(Site, null=True, blank=True, related_name='site_roles')
    project = models.ForeignKey(Project, null=True, blank=True, related_name='project_roles')
    organization = models.ForeignKey(Organization, null=True, blank=True, related_name='organization_roles')

    def __unicode__(self):
        return 'user: {}\'s role : {}'.format(self.user.__unicode__(), self.group.__unicode__())

    class Meta:
        unique_together = ('user', 'group', 'organization', 'project','site')

    def clean(self):
        if self.group.name == 'Site Supervisor' and not self.site_id:
            raise ValidationError({
                'site': ValidationError(_('Missing site.'), code='required'),
            })
        if self.group.name == 'Central Engineer' and not self.site_id:
            raise ValidationError({
                'site': ValidationError(_('Missing site.'), code='required'),
            })

        if self.group.name == 'Project Manager' and not self.project_id:
            raise ValidationError({
                'project': ValidationError(_('Missing Project.'), code='required'),
            })

        if self.group.name == 'Organization Admin' and not self.organization_id:
            raise ValidationError({
                'organization': ValidationError(_('Missing Organization.'), code='required'),
            })

    def save(self, *args, **kwargs):
        if self.group.name == 'Super Admin':
            self.organization = None
            self.project = None
            self.site = None
        elif self.group.name == 'Organization Admin':
            self.project = None
            self.site = None
        elif self.group.name == 'Project Manager':
            self.site = None
            self.organization = self.project.organization

        elif self.group.name == 'Site Supervisor':
            self.project = self.site.project
            self.organization = self.site.project.organization

        elif self.group.name == 'Central Engineer':
            self.project = self.site.project
            self.organization = self.site.project.organization
        super(UserRole, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        if self.group.name == 'Super Admin':
            self.organization = None
            self.project = None
            self.site = None
        elif self.group.name == 'Organization Admin':
            self.project = None
            self.site = None
        elif self.group.name == 'Project Manager':
            self.site = None
            self.organization = self.project.organization

        elif self.group.name == 'Site Supervisor':
            self.project = self.site.project
            self.organization = self.site.project.organization

        elif self.group.name == 'Central Engineer':
            self.project = self.site.project
            self.organization = self.site.project.organization
        super(UserRole, self).update(*args, **kwargs)

    @staticmethod
    def is_active(user,group):
        return UserRole.objects.filter(user=user, group=group,ended_date=None).count()

    @staticmethod
    def get_active_roles(user):
        return UserRole.objects.filter(user=user,ended_at=None).select_related('group', 'organization')
