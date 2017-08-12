from functools import wraps

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
from django.views.generic.edit import UpdateView as BaseUpdateView, CreateView as BaseCreateView, DeleteView as BaseDeleteView
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from onadata.apps.fieldsight.models import Organization, Project, Site
from onadata.apps.users.models import UserProfile
from .helpers import json_from_object
from onadata.apps.userrole.models import UserRole

class OrganizationMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.role.group.name == "Super Admin":
                return super(OrganizationMixin, self).dispatch(request, *args, **kwargs)
            organization_id = self.kwargs.get('pk')
            user_id = request.user.id
            user_role = request.roles.filter(organization_id = organization_id)
            if user_role and user_role[0].group.name == "Organization Admin":
                return super(OrganizationMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()


class ProjectMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):

        if request.group.name == "Super Admin":
            return super(ProjectMixin, self).dispatch(request, *args, **kwargs)
        
        project_id = self.kwargs.get('pk')
        user_id = request.user.id
        user_role = request.roles.filter(user_id = user_id, project_id = project_id)
        
        if user_role and user_role[0].group.name == "Project Manager":
            return super(ProjectMixin, self).dispatch(request, *args, **kwargs)
        organization_id = Project.objects.get(pk=project_id).organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id)
        
        if user_role_asorgadmin and user_role_asorgadmin[0].group.name == "Organization Admin":
            return super(ProjectMixin, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()

class ReviewerMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):

        if request.group.name == "Super Admin":
            return super(ProjectMixin, self).dispatch(request, *args, **kwargs)
        
        site_id = self.kwargs.get('pk')
        user_id = request.user.id
        user_role = request.roles.filter(user_id = user_id, site_id = site_id, group__name="Reviewer")
        
        if user_role:
            return super(ProjectMixin, self).dispatch(request, *args, **kwargs)
        
        project = Site.objects.get(pk=ste_id).project
        user_role_aspadmin = request.roles.filter(user_id = user_id, project_id = project.id, group__name="Project Manager")
        if user_role_aspadmin:
            return super(ProjectMixin, self).dispatch(request, *args, **kwargs)

        organization_id = project.organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id)
        if user_role_asorgadmin and user_role_asorgadmin[0].group.name == "Organization Admin":
            return super(ProjectMixin, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()