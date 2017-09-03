from django.contrib import admin
from .models import UserInvite, Organization

admin.site.register(UserInvite)
admin.site.register(Organization)