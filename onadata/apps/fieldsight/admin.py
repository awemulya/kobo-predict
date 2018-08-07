from django.contrib import admin
from .models import UserInvite, Organization, Project, Site, Region, SiteType, OrganizationType, ProjectType

admin.site.register(UserInvite)
admin.site.register(Organization)
admin.site.register(Project)
admin.site.register(Site)
admin.site.register(Region)
admin.site.register(SiteType)
admin.site.register(OrganizationType)
admin.site.register(ProjectType)