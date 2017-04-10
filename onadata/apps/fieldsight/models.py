from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models import GeoManager
from django.core.urlresolvers import reverse
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.utils.text import slugify
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

# classs common(abstract)


class Organization(models.Model):
    name = models.CharField("Organization Name", max_length=255)
    type = models.ForeignKey(OrganizationType, verbose_name='Type of Organization')
    phone = models.CharField("Contact Number",max_length=255, blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    country = models.CharField(max_length=3, choices=COUNTRIES, default=u'NPL')
    address = models.TextField(blank=True, null=True)
    public_desc = models.TextField("Public Description", blank=True, null=True)
    additional_desc = models.TextField("Additional Description", blank=True, null=True)
    logo = models.ImageField(upload_to="logo", default="logo/default_org.png")
    is_active = models.BooleanField(default=True)
    location = PointField(geography=True, srid=4326, blank=True, null=True,)

    class Meta:
         ordering = ['-is_active', 'name', ]

    def __unicode__(self):
        return u'{}'.format(self.name)

    objects = GeoManager()

    @property
    def latitude(self):
        if self.location:
            return self.location.y

    @property
    def longitude(self):
        if self.location:
            return self.location.x

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('organizations-detail', kwargs={'pk': self.pk})

    @property
    def get_staffs(self):
        staffs = self.organization_roles.filter(group__name="Organization Admin").values_list('id', 'user__username')
        return staffs\

    @property
    def get_staffs_org(self):
        staffs = self.organization_roles.filter(group__name="Organization Admin")
        return staffs

    @property
    def get_staffs_id(self):
        return self.organization_roles.filter(group__name="Organization Admin").values_list('id', flat=True)

    def get_organization_type(self):
        return self.type.name


class Project(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(ProjectType, verbose_name='Type of Project')
    phone = models.CharField(max_length=255, blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    donor = models.CharField(max_length=256, blank=True, null=True)
    public_desc = models.TextField("Public Description", blank=True, null=True)
    additional_desc = models.TextField("Additional Description", blank=True, null=True)
    organization = models.ForeignKey(Organization, related_name='projects')
    logo = models.ImageField(upload_to="logo", default="logo/default_org.png")
    is_active = models.BooleanField(default=True)
    location = PointField(geography=True, srid=4326, blank=True, null=True)

    objects = GeoManager()

    class Meta:
         ordering = ['-is_active', 'name', ]

    @property
    def latitude(self):
        if self.location:
            return self.location.y

    @property
    def longitude(self):
        if self.location:
            return self.location.x

    def __str__(self):
        return self.name

    @property
    def get_staffs(self):
        staffs = self.project_roles.filter(group__name__in=["Reviewer", "Project Manager"])
        return staffs

    @property
    def get_staffs_both_role(self):
        managers_id = self.project_roles.filter(group__name="Project Manager").values_list('user__id', flat=True)
        reviewers_id = self.project_roles.filter(group__name="Reviewer").values_list('user__id', flat=True)
        both = list(set(managers_id).intersection(reviewers_id))
        return both


    def get_organization_name(self):
        return self.organization.name

    def get_project_type(self):
        return self.type.name

    def get_submissions_count(self):
        outstanding = self.project_instances.filter(form_status=0).count()
        rejected = self.project_instances.filter(form_status=1).count()
        flagged = self.project_instances.filter(form_status=2).count()
        approved = self.project_instances.filter(form_status=3).count()

        return outstanding, flagged, approved, rejected

    def get_absolute_url(self):
        return reverse('projects-detail', kwargs={'pk': self.pk})


class Site(models.Model):
    identifier = models.CharField("ID", max_length=255)
    name = models.CharField(max_length=255)
    type = models.ForeignKey(ProjectType, verbose_name='Type of Site')
    phone = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    public_desc = models.TextField("Public Description", blank=True, null=True)
    additional_desc = models.TextField("Additional Description", blank=True, null=True)
    project = models.ForeignKey(Project, related_name='sites')
    logo = models.ImageField(upload_to="logo", default="logo/default_site.png")
    is_active = models.BooleanField(default=True)
    location = PointField(geography=True, srid=4326, blank=True, null=True)

    objects = GeoManager()

    class Meta:
         ordering = ['-is_active', 'name', ]
         unique_together = [('identifier', 'project'), ]

    @property
    def latitude(self):
        if self.location:
            return self.location.y

    @property
    def longitude(self):
        if self.location:
            return self.location.x

    def __str__(self):
        return self.name

    @property
    def get_supervisors(self):
        return self.site_roles.all()


    @property
    def get_supervisor_id(self):
        staffs = list(self.site_roles.filter(group__name="Site Supervisor"))
        if staffs:
            return [role.user.id for role in staffs]
        return []

    def get_organization_name(self):
        return self.project.organization.name

    def get_project_name(self):
        return self.project.name

    def get_site_type(self):
        return self.type.name

    def progress(self):
        stages = self.site_forms.filter(xf__isnull=False, is_staged=True).count()
        approved = self.site_instances.filter(form_status=3, site_fxf__is_staged=True).count()
        if not approved:
            return 0
        if not stages:
            return 0
        p = ("%.0f" % (approved/(stages*0.01)))
        p = int(p)
        if p > 99:
            return 100
        return p

    def get_site_submission(self):
        instances = self.site_instances.all()
        outstanding, flagged, approved, rejected = [], [], [], []
        for submission in instances:
            if submission.form_status == 0:
                outstanding.append(submission)
            elif submission.form_status == 1:
                rejected.append(submission)
            elif submission.form_status == 2:
                flagged.append(submission)
            elif submission.form_status == 3:
                approved.append(submission)

        return outstanding, flagged, approved, rejected

    @property
    def get_absolute_url(self):
        return reverse('sites-detail', kwargs={'pk': self.pk})


def get_image_filename(instance, filename):
    title = instance.site.identifier
    project = instance.site.project.pk
    slug = slugify(title)
    return "blueprint_images/%s-%s-%s" % (project, slug, filename)


class BluePrints(models.Model):
    site = models.ForeignKey(Site, related_name="blueprints")
    image = models.ImageField(upload_to=get_image_filename,
                              verbose_name='BluePrints',)
