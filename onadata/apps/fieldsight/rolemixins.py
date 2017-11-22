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


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwargs):
        view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        return login_required(view)


class OrganizationRoleMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.role.group.name == "Super Admin":
                return super(OrganizationRoleMixin, self).dispatch(request, *args, **kwargs)
            organization_id = self.kwargs.get('pk')
            user_id = request.user.id
            user_role = request.roles.filter(organization_id = organization_id, group__name="Organization Admin")
            if user_role:
                return super(OrganizationRoleMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()


class ProjectRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):

        if request.group.name == "Super Admin":
            return super(ProjectRoleMixin, self).dispatch(request, *args, **kwargs)
        
        project_id = self.kwargs.get('pk')
        user_id = request.user.id
        user_role = request.roles.filter(user_id = user_id, project_id = project_id, group__name="Project Manager")
        
        if user_role:
            return super(ProjectRoleMixin, self).dispatch(request, *args, **kwargs)
        organization_id = Project.objects.get(pk=project_id).organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group__name="Organization Admin")
        
        if user_role_asorgadmin:
            return super(ProjectRoleMixin, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()

class ReviewerRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):

        if request.group.name == "Super Admin":
            return super(ReviewerRoleMixin, self).dispatch(request, *args, **kwargs)
        
        site_id = self.kwargs.get('pk')
        user_id = request.user.id
        user_role = request.roles.filter(user_id = user_id, site_id = site_id, group__name="Reviewer")
        
        if user_role:
            return super(ReviewerRoleMixin, self).dispatch(request, *args, **kwargs)
        
        project = Site.objects.get(pk=site_id).project
        user_role_aspadmin = request.roles.filter(user_id = user_id, project_id = project.id, group__name="Project Manager")
        if user_role_aspadmin:
            return super(ReviewerRoleMixin, self).dispatch(request, *args, **kwargs)

        organization_id = project.organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group__name="Organization Admin")
        if user_role_asorgadmin:
            return super(ReviewerRoleMixin, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()

class SiteSupervisorRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):

        if request.group.name == "Super Admin":
            return super(ReviewerRoleMixin, self).dispatch(request, *args, **kwargs)
        
        site_id = self.kwargs.get('pk')
        user_id = request.user.id
        user_role = request.roles.filter(user_id = user_id, site_id = site_id, group__name="Site Supervisor")
        
        if user_role:
            return super(SiteSupervisorRoleMixin, self).dispatch(request, *args, **kwargs)
        
        project = Site.objects.get(pk=site_id).project
        user_role_aspadmin = request.roles.filter(user_id = user_id, project_id = project.id, group__name="Project Manager")
        if user_role_aspadmin:
            return super(SiteSupervisorRoleMixin, self).dispatch(request, *args, **kwargs)

        organization_id = project.organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group__name="Organization Admin")
        if user_role_asorgadmin:
            return super(SiteSupervisorRoleMixin, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()

class SiteDeleteRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):

        if request.group.name == "Super Admin":
            return super(ReviewerRoleMixin, self).dispatch(request, *args, **kwargs)
        
        site_id = self.kwargs.get('pk')
        user_id = request.user.id
        
        project = Site.objects.get(pk=site_id).project
        user_role_aspadmin = request.roles.filter(user_id = user_id, project_id = project.id, group__name="Project Manager")
        if user_role_aspadmin:
            return super(SiteDeleteRoleMixin, self).dispatch(request, *args, **kwargs)

        organization_id = project.organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group__name="Organization Admin")
        if user_role_asorgadmin:
            return super(SiteDeleteRoleMixin, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()



class ProjectRoleMixinDeleteView(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):

        if request.group.name == "Super Admin":
            return super(ProjectRoleMixinDeleteView, self).dispatch(request, *args, **kwargs)
        
        project_id = self.kwargs.get('pk')
        user_id = request.user.id

        organization_id = Project.objects.get(pk=project_id).organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group__name="Organization Admin")
        
        if user_role_asorgadmin:
            return super(ProjectRoleMixinDeleteView, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()

class ReviewerRoleMixinDeleteView(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):

        if request.group.name == "Super Admin":
            return super(ReviewerRoleMixinDeleteView, self).dispatch(request, *args, **kwargs)
        
        site_id = self.kwargs.get('pk')
        user_id = request.user.id
        
        user_role = request.roles.filter(user_id = user_id, site_id = site_id, group__name="Reviewer")
        
        if user_role:
            return super(SiteSupervisorRoleMixin, self).dispatch(request, *args, **kwargs)
        project = Site.objects.get(pk=site_id).project
        user_role_aspadmin = request.roles.filter(user_id = user_id, project_id = project.id, group__name="Project Manager")
        if user_role_aspadmin:
            return super(ReviewerRoleMixinDeleteView, self).dispatch(request, *args, **kwargs)

        organization_id = project.organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group__name="Organization Admin")
        if user_role_asorgadmin:
            return super(ReviewerRoleMixinDeleteView, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()


class ProjectRoleView(LoginRequiredMixin):
    def form_valid(self, form):
        if self.request.kwargs.get('pk'):
            form.instance.project = self.request.kwargs.get('pk')
        return super(ProjectRoleView, self).form_valid(form)

    def get_queryset(self):
        return super(ProjectRoleView, self).get_queryset()



