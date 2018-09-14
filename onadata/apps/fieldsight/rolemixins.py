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

from onadata.apps.fieldsight.models import Organization, Project, Site
from onadata.apps.fsforms.models import FieldSightXF, FInstance 
from onadata.apps.users.models import UserProfile
from .helpers import json_from_object
from onadata.apps.userrole.models import UserRole
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from django.db.models import Q
from onadata.apps.logger.models import XForm



# ConditionalFormMixin =  Returns whether the user has full acess or readonly access through "is_readonly" attribute which is either True or False for a specific form. The url parameter should have "fsxf_id" which is form id.
# SPFMixin = Site, Project mixin needs two parameters in url "is_project" and "pk" which can be site_id or project_id. It checks permission for resppective pk depending upon "is_project" attribute from url.
# Readonly site/project levelMixin = It checks if user has access to just view certain pages/view. 

# Important , in near future roles should be cached or some similar alternatives should be added.


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwargs):
        view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        return login_required(view)


class OrganizationRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(OrganizationRoleMixin, self).dispatch(request, *args, **kwargs)
        organization_id = self.kwargs.get('pk')
        user_id = request.user.id
        user_role = request.roles.filter(organization_id = organization_id, group_id=1)
        if user_role:
            return super(OrganizationRoleMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()


class SuperUserRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(SuperUserRoleMixin, self).dispatch(request, *args, **kwargs)    
        raise PermissionDenied()


class ProjectRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(ProjectRoleMixin, self).dispatch(request, *args, **kwargs)
        
        project_id = self.kwargs.get('pk')
        user_id = request.user.id
        user_role = request.roles.filter(user_id = user_id, project_id = project_id, group_id=2)
        
        if user_role:
            return super(ProjectRoleMixin, self).dispatch(request, *args, **kwargs)
        organization_id = Project.objects.get(pk=project_id).organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group_id=1)
        
        if user_role_asorgadmin:
            return super(ProjectRoleMixin, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()
#use when project role and doner role is required mostly it is like readonly because doner is only allowed to read only
class ReadonlyProjectLevelRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(ReadonlyProjectLevelRoleMixin, self).dispatch(request, is_donor_only=False, *args, **kwargs)
        
        project_id = self.kwargs.get('pk')
        user_id = request.user.id
        user_role = request.roles.filter(project_id = project_id, group_id=2)
        
        if user_role:
            return super(ReadonlyProjectLevelRoleMixin, self).dispatch(request, is_donor_only=False, *args, **kwargs)

        organization_id = Project.objects.get(pk=project_id).organization.id
        user_role_asorgadmin = request.roles.filter(organization_id = organization_id, group_id=1)
        
        if user_role_asorgadmin:
            return super(ReadonlyProjectLevelRoleMixin, self).dispatch(request, is_donor_only=False, *args, **kwargs)

        user_role_asdonor = request.roles.filter(project_id = project_id, group_id=7)
        if user_role_asdonor:
            return super(ReadonlyProjectLevelRoleMixin, self).dispatch(request, is_donor_only=True, *args, **kwargs)

        raise PermissionDenied()

class ReadonlySiteLevelRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):

        if request.group.name == "Super Admin":
            return super(ReadonlySiteLevelRoleMixin, self).dispatch(request, is_donor_only=False, *args, **kwargs)
        
        site_id = self.kwargs.get('pk')
        user_id = request.user.id
        user_role = request.roles.filter(user_id = user_id, site_id = site_id, group_id__in=[3,4])
        
        if user_role:
            return super(ReadonlySiteLevelRoleMixin, self).dispatch(request, is_donor_only=False, *args, **kwargs)
        
        project = Site.objects.get(pk=site_id).project
        user_role_aspadmin = request.roles.filter(user_id = user_id, project_id = project.id, group_id=2)
        if user_role_aspadmin:
            return super(ReadonlySiteLevelRoleMixin, self).dispatch(request, is_donor_only=False, *args, **kwargs)

        organization_id = project.organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group_id=1)
        if user_role_asorgadmin:
            return super(ReadonlySiteLevelRoleMixin, self).dispatch(request, is_donor_only=False, *args, **kwargs)

        user_role_asdonor = request.roles.filter(user_id = user_id, project_id = project.id, group_id=7)
        if user_role_asdonor:
            return super(ReadonlySiteLevelRoleMixin, self).dispatch(request, is_donor_only=True, *args, **kwargs)

        raise PermissionDenied()

#use when doner role is required to load site dashboard
class DonorSiteViewRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(DonorSiteViewRoleMixin, self).dispatch(request, *args, **kwargs)
        
        site = get_object_or_404(Site, pk=self.kwargs.get('pk'))
        user_id = request.user.id
        user_role = request.roles.filter(user_id = user_id, project_id = site.project_id, group_id=7)
        
        if user_role:
            return super(DonorSiteViewRoleMixin, self).dispatch(request, *args, **kwargs)
        organization_id = Project.objects.get(pk=site.project_id).organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group_id=1)
        
        if user_role_asorgadmin:
            return super(DonorSiteViewRoleMixin, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()

# Use when doner role is required to load donor dashboard
class DonorRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(DonorRoleMixin, self).dispatch(request, *args, **kwargs)
        
        project_id = self.kwargs.get('pk')
        user_id = request.user.id
        user_role = request.roles.filter(user_id = user_id, project_id = project_id, group_id=7)
        
        if user_role:
            return super(DonorRoleMixin, self).dispatch(request, *args, **kwargs)
        organization_id = Project.objects.get(pk=project_id).organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group_id=1)
        
        if user_role_asorgadmin:
            return super(DonorRoleMixin, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()

class ReviewerRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):

        if request.group.name == "Super Admin":
            return super(ReviewerRoleMixin, self).dispatch(request, *args, **kwargs)
        
        site_id = self.kwargs.get('pk')
        user_id = request.user.id
        user_role = request.roles.filter(user_id = user_id, site_id = site_id, group_id=3)
        
        if user_role:
            return super(ReviewerRoleMixin, self).dispatch(request, *args, **kwargs)
        
        project = Site.objects.get(pk=site_id).project
        user_role_aspadmin = request.roles.filter(user_id = user_id, project_id = project.id, group_id=2)
        if user_role_aspadmin:
            return super(ReviewerRoleMixin, self).dispatch(request, *args, **kwargs)

        organization_id = project.organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group_id=1)
        if user_role_asorgadmin:
            return super(ReviewerRoleMixin, self).dispatch(request, *args, **kwargs)

        # user_role_asSs = request.roles.filter(user_id = user_id, site_id = site_id, group__name="Site Supervisor")
        # if user_roleas_Ss:


        raise PermissionDenied()

class SiteRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):

        if request.group.name == "Super Admin":
            return super(SiteRoleMixin, self).dispatch(request, is_supervisor_only=False, *args, **kwargs)
        
        site_id = self.kwargs.get('pk')
        user_id = request.user.id
        user_role = request.roles.filter(site_id = site_id, group_id=3)
        
        if user_role:
            return super(SiteRoleMixin, self).dispatch(request, is_supervisor_only=False, *args, **kwargs)
        
        project = Site.objects.get(pk=site_id).project
        user_role_aspadmin = request.roles.filter(project_id = project.id, group_id=2)
        if user_role_aspadmin:
            return super(SiteRoleMixin, self).dispatch(request, is_supervisor_only=False, *args, **kwargs)

        organization_id = project.organization.id
        user_role_asorgadmin = request.roles.filter(organization_id = organization_id, group_id=1)
        if user_role_asorgadmin:
            return super(SiteRoleMixin, self).dispatch(request, is_supervisor_only=False, *args, **kwargs)

        user_role = request.roles.filter(site_id = site_id, group_id=4)
        if user_role:
            return super(SiteRoleMixin, self).dispatch(request, is_supervisor_only=True, *args, **kwargs)

        raise PermissionDenied()

class SiteDeleteRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):

        if request.group.name == "Super Admin":
            return super(SiteDeleteRoleMixin, self).dispatch(request, *args, **kwargs)
        
        site_id = self.kwargs.get('pk')
        user_id = request.user.id
        
        project = Site.objects.get(pk=site_id).project
        user_role_aspadmin = request.roles.filter(user_id = user_id, project_id = project.id, group_id=2)
        
        if user_role_aspadmin:
            return super(SiteDeleteRoleMixin, self).dispatch(request, *args, **kwargs)

        organization_id = project.organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group_id=1)
        
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
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group_id=1)
        
        if user_role_asorgadmin:
            return super(ProjectRoleMixinDeleteView, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()

class ReviewerRoleMixinDeleteView(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):

        if request.group.name == "Super Admin":
            return super(ReviewerRoleMixinDeleteView, self).dispatch(request, *args, **kwargs)
        
        site_id = self.kwargs.get('pk')
        user_id = request.user.id
        
        user_role = request.roles.filter(user_id = user_id, site_id = site_id, group_id=3)
        
        if user_role:
            return super(SiteSupervisorRoleMixin, self).dispatch(request, *args, **kwargs)
        project = Site.objects.get(pk=site_id).project
        user_role_aspadmin = request.roles.filter(user_id = user_id, project_id = project.id, group_id=2)
        if user_role_aspadmin:
            return super(ReviewerRoleMixinDeleteView, self).dispatch(request, *args, **kwargs)

        organization_id = project.organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group_id=1)
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



class SPFmixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.group.name == "Super Admin":
                return super(SPFmixin, self).dispatch(request, *args, **kwargs)

        user_id = request.user.id

        if self.kwargs.get('is_project') == '0':
            site_id = self.kwargs.get('pk')
            user_role = request.roles.filter(user_id = user_id, site_id = site_id, group_id=3)
            if user_role:
                return super(SPFmixin, self).dispatch(request, *args, **kwargs)
            project_id=Site.objects.get(pk=site_id).project.id
        
        else:
            project_id = self.kwargs.get('pk')

        user_role = request.roles.filter(user_id = user_id, project_id = project_id, group_id=2)
        if user_role:
            return super(SPFmixin, self).dispatch(request, *args, **kwargs)

        organization_id = Project.objects.get(pk=project_id).organization.id
        user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group_id=1)
        if user_role_asorgadmin:
            return super(SPFmixin, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()    


class FormMixin(LoginRequiredMixin):
    def dispatch(self, request, fsxf_id, *args, **kwargs):
        if request.group.name == "Super Admin":
                return super(FormMixin, self).dispatch(request, fsxf_id, *args, **kwargs)

        user_id = request.user.id
        form = get_object_or_404(FieldSightXF, pk=fsxf_id)

        if form.site is not None:
            site_id = form.site.id
            user_role = request.roles.filter(site_id = site_id, group_id=3)
            if user_role:
                return super(FormMixin, self).dispatch(request, fsxf_id, *args, **kwargs)
            project_id=Site.objects.get(pk=site_id).project.id
        
        else:
            project_id = form.project.id

        user_role = request.roles.filter(project_id = project_id, group_id=2)
        if user_role:
            return super(FormMixin, self).dispatch(request, fsxf_id, *args, **kwargs)

        organization_id = Project.objects.get(pk=project_id).organization.id
        user_role_asorgadmin = request.roles.filter(organization_id = organization_id, group_id=1)
        if user_role_asorgadmin:
            return super(FormMixin, self).dispatch(request, fsxf_id, *args, **kwargs)

        raise PermissionDenied()   

class ReadonlyFormMixin(LoginRequiredMixin):
    def dispatch(self, request, fsxf_id, *args, **kwargs):
        if request.group.name == "Super Admin":
                return super(ReadonlyFormMixin, self).dispatch(request, fsxf_id, *args, **kwargs)

        user_id = request.user.id
        form = get_object_or_404(FieldSightXF, pk=fsxf_id)

        if form.site is not None:
            site_id = form.site.id
            user_role = request.roles.filter(site_id = site_id, group_id__in=[3,4])
            if user_role:
                return super(ReadonlyFormMixin, self).dispatch(request, fsxf_id, *args, **kwargs)
            project_id=Site.objects.get(pk=site_id).project.id
        
        else:
            project_id = form.project.id

        user_role = request.roles.filter(project_id = project_id, group_id__in=[2,7])
        if user_role:
            return super(ReadonlyFormMixin, self).dispatch(request, fsxf_id, *args, **kwargs)

        organization_id = Project.objects.get(pk=project_id).organization.id
        user_role_asorgadmin = request.roles.filter(organization_id = organization_id, group_id = 1)
        if user_role_asorgadmin:
            return super(ReadonlyFormMixin, self).dispatch(request, fsxf_id, *args, **kwargs)

        raise PermissionDenied()   


#whwerver only readonly permissions are required for urls which includes fsxf_id, this mixin can be used. The function
#returns "is_readonly" attribute either True or False so make sure to use it to determine readonly features in view or template.
class ConditionalFormMixin(LoginRequiredMixin):
    def dispatch(self, request, fsxf_id, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(ConditionalFormMixin, self).dispatch(request, fsxf_id, is_read_only= False, *args, **kwargs)

        user_id = request.user.id
        form = get_object_or_404(FieldSightXF, pk=fsxf_id)

        if form.site is not None:
            site_id = form.site.id
            user_role = request.roles.filter(site_id = site_id, group_id=3)
            if user_role:
                return super(ConditionalFormMixin, self).dispatch(request, fsxf_id, is_read_only= False, *args, **kwargs)
            project_id=form.site.project_id
        
        else:
            project_id = form.project.id

        user_role = request.roles.filter(project_id = project_id, group_id=2)
        if user_role:
            return super(ConditionalFormMixin, self).dispatch(request, fsxf_id, is_read_only= False, *args, **kwargs)

        organization_id = Project.objects.get(pk=project_id).organization.id
        user_role_asorgadmin = request.roles.filter(organization_id = organization_id, group_id=1)
        if user_role_asorgadmin:
            return super(ConditionalFormMixin, self).dispatch(request, fsxf_id, is_read_only= False, *args, **kwargs)
        if form.site is not None:
            user_role = request.roles.filter(Q(site_id = form.site_id, group_id=4) | Q(project_id = form.site.project_id, group_id=7))
        else:
            user_role = request.roles.filter(project_id = form.project_id, group_id=7)
        if user_role:
            return super(ConditionalFormMixin, self).dispatch(request, fsxf_id, is_read_only= True, *args, **kwargs)

        raise PermissionDenied()   






class MyFormMixin(LoginRequiredMixin):
    def dispatch(self, request, xf_id, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(MyFormMixin, self).dispatch(request, xf_id, *args, **kwargs)

        user_id = request.user.id
        xform = get_object_or_404(XForm, pk=xf_id)

        if xform.user_id == user_id:
            return super(MyFormMixin, self).dispatch(request, xf_id, *args, **kwargs)

        raise PermissionDenied()

class EndRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(EndRoleMixin, self).dispatch(request, *args, **kwargs)
        role_to_end = UserRole.objects.get(pk=self.kwargs.get('pk'))
        if role_to_end.group_id == 2:
            user_role = request.roles.filter(organization_id = role_to_end.organization_id, group_id=1)
            if user_role:
                return super(EndRoleMixin, self).dispatch(request, *args, **kwargs)
        
        elif role_to_end.group_id == 3 or role_to_end.group_id == 4:
            user_role = request.roles.filter(Q(project_id = role_to_end.project_id, group_id=2) | Q(organization_id = role_to_end.organization_id, group_id=1))
            if user_role:
                return super(EndRoleMixin, self).dispatch(request, *args, **kwargs)     
        raise PermissionDenied() 


class FInstanceRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(FInstanceRoleMixin, self).dispatch(request, *args, **kwargs)
        finstance = get_object_or_404(FInstance, instance_id=self.kwargs.get('instance_pk'))
        if finstance.site or finstance.project:
            user_id = request.user.id
            project = finstance.project
            if finstance.site:
                site_id = finstance.site.id
                
                user_role = request.roles.filter(site_id = site_id, group_id=3)
                
                if user_role:
                    return super(FInstanceRoleMixin, self).dispatch(request, *args, **kwargs)
                
                user_role_aspadmin = request.roles.filter(project_id = finstance.site.project_id, group_id=2)
                if user_role_aspadmin:
                    return super(FInstanceRoleMixin, self).dispatch(request, *args, **kwargs)

                organization_id = finstance.site.project.organization_id
                user_role_asorgadmin = request.roles.filter(organization_id = organization_id, group_id=1)
                
                if user_role_asorgadmin:
                    return super(FInstanceRoleMixin, self).dispatch(request, *args, **kwargs)
                project = finstance.site.project
            
            if project:
                user_role_aspadmin = request.roles.filter(project_id = project.id, group_id=2)
                if user_role_aspadmin:
                    return super(FInstanceRoleMixin, self).dispatch(request, *args, **kwargs)
                organization_id = project.organization.id
                user_role_asorgadmin = request.roles.filter(organization_id = organization_id, group_id=1)
                if user_role_asorgadmin:
                    return super(FInstanceRoleMixin, self).dispatch(request, *args, **kwargs)
            
        raise PermissionDenied() 


class FullMapViewMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(FullMapViewMixin, self).dispatch(request, *args, **kwargs)
            
        user_id = request.user.id
        user_role = request.roles.filter(user_id = user_id, group_id__in=[7, 1, 2])
        
        if user_role:
            return super(FullMapViewMixin, self).dispatch(request, *args, **kwargs)
        
        raise PermissionDenied()

# for api mixins/permissions

# class ProjectPermission(BasePermission):
#     def has_permission(self, request, view):
#         if request.group.name == "Super Admin":
#             return super(ProjectRoleMixin, self).dispatch(request, *args, **kwargs)
        
#         project_id = self.kwargs.get('pk')
#         user_id = request.user.id
#         user_role = request.roles.filter(user_id = user_id, project_id = project_id, group__name="Project Manager")
        
#         if user_role:
#             return True
        
#         organization_id = Project.objects.get(pk=project_id).organization.id
#         user_role_asorgadmin = request.roles.filter(user_id = user_id, organization_id = organization_id, group__name="Organization Admin")
        
#         if user_role_asorgadmin:
#             return True

#         return False
                
                    


