from django.contrib import admin
from .models import UserInvite, Organization, Project

admin.site.register(UserInvite)
admin.site.register(Organization)
admin.site.register(Project)