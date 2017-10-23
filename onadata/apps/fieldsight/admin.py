from django.contrib import admin
from .models import UserInvite, Organization, Project, Site

admin.site.register(UserInvite)
admin.site.register(Organization)
admin.site.register(Project)
admin.site.register(Site)