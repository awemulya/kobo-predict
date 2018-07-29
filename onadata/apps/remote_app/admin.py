from django.contrib import admin
from .models import RemoteApp, ConnectedProject, ConnectedDomain


class ConnectedProjectInline(admin.TabularInline):
    model = ConnectedProject
    extra = 0


class ConnectedDomainInine(admin.TabularInline):
    model = ConnectedDomain
    extra = 0


@admin.register(RemoteApp)
class RemoteAppAdmin(admin.ModelAdmin):
    inlines = [
        ConnectedProjectInline,
        ConnectedDomainInine,
    ]
    readonly_fields = ['auth_user', 'token']
