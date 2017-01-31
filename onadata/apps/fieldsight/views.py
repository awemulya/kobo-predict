from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.views.generic import ListView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize

from registration.backends.default.views import RegistrationView

from onadata.apps.fsforms.Submission import Submission
from onadata.apps.fsforms.models import FieldSightXF
from onadata.apps.userrole.models import UserRole
from onadata.apps.users.models import UserProfile
from .mixins import (LoginRequiredMixin, SuperAdminMixin, OrganizationMixin, ProjectMixin,
                     CreateView, UpdateView, DeleteView, OrganizationView as OView, ProjectView as PView,
                     group_required, OrganizationViewFromProfile)
from .models import Organization, Project, Site, ExtraUserDetail
from .forms import OrganizationForm, ProjectForm, SiteForm, RegistrationForm, SetOrgAdminForm, \
    SetProjectManagerForm, SetSupervisorForm, SetCentralEngForm, AssignOrgAdmin


@login_required
def dashboard(request):
    if UserRole.is_active(request.user, "Super Admin"):
        return HttpResponseRedirect(reverse("fieldsight:organizations-list"))
    elif UserRole.is_active(request.user, "Organization Admin"):
        org = UserRole.objects.filter(user=request.user, group__name="Organization Admin")[0].organization
        return HttpResponseRedirect(reverse("fieldsight:organization-dashboard", kwargs={'pk': org.pk}))
    elif UserRole.is_active(request.user, "Project Manager"):
        project = UserRole.objects.filter(user=request.user, group__name="Project Manager")[0].project
        return HttpResponseRedirect(reverse("fieldsight:project-dashboard", kwargs={'pk': project.pk}))
    elif UserRole.is_active(request.user, "Site Supervisor"):
        site = UserRole.objects.filter(user=request.user, group__name="Site Supervisor")[0].site
        return HttpResponseRedirect(reverse("fieldsight:site-dashboard", kwargs={'pk': site.pk}))
    total_users = User.objects.all().count()
    total_organizations = Organization.objects.all().count()
    total_projects = Project.objects.all().count()
    total_sites = Site.objects.all().count()
    data = serialize('geojson', Site.objects.all(), geometry_field='location',
                        fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone',))
    fs_forms = FieldSightXF.objects.all()
    fs_forms = list(fs_forms)
    outstanding = flagged = approved = rejected = 0
    for form in fs_forms:
        if form.form_status == 0:
            outstanding += 1
        elif form.form_status == 1:
            flagged +=1
        elif form.form_status == 2:
            approved +=1
        else:
            rejected +=1

    dashboard_data = {
        'total_users': total_users,
        'total_organizations': total_organizations,
        'total_projects': total_projects,
        'total_sites': total_sites,
        'outstanding': outstanding,
        'flagged': flagged,
        'approved': approved,
        'rejected': rejected,
        'data': data,
    }
    return TemplateResponse(request, "fieldsight/fieldsight_dashboard.html", dashboard_data)



@login_required
def organization_dashboard(request, pk):
    obj = Organization.objects.get(pk=pk)
    peoples_involved = User.objects.filter(user_profile__organization=obj)
    sites = Site.objects.filter(project__organization=obj)
    data = serialize('geojson', sites, geometry_field='location',
                     fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone',))

    projects = Project.objects.filter(organization=obj)
    total_projects = len(projects)
    total_sites = len(sites)
    fs_forms = FieldSightXF.objects.filter(site__project__organization=obj.id)
    fs_forms = list(fs_forms)
    outstanding = flagged = approved = rejected = 0
    for form in fs_forms:
        if form.form_status == 0:
            outstanding += 1
        elif form.form_status == 1:
            flagged +=1
        elif form.form_status == 2:
            approved +=1
        else:
            rejected +=1

    dashboard_data = {
        'obj': obj,
        'projects': projects,
        'sites': sites,
        'peoples_involved': peoples_involved,
        'total_projects': total_projects,
        'total_sites': total_sites,
        'outstanding': outstanding,
        'flagged': flagged,
        'approved': approved,
        'rejected': rejected,
        'data': data,
    }
    return TemplateResponse(request, "fieldsight/organization_dashboard.html", dashboard_data)

@login_required
def project_dashboard(request, pk):
    obj = Project.objects.get(pk=pk)
    peoples_involved = User.objects.filter(user_profile__organization=obj.organization)
    sites = Site.objects.filter(project=obj)
    data = serialize('geojson', sites, geometry_field='location',
                     fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone',))

    total_sites = len(sites)
    fs_forms = FieldSightXF.objects.filter(site__project=obj.id)
    fs_forms = list(fs_forms)
    outstanding = flagged = approved = rejected = 0
    for form in fs_forms:
        if form.form_status == 0:
            outstanding += 1
        elif form.form_status == 1:
            flagged +=1
        elif form.form_status == 2:
            approved +=1
        else:
            rejected +=1

    dashboard_data = {
        'obj': obj,
        'sites': sites,
        'peoples_involved': peoples_involved,
        'total_sites': total_sites,
        'outstanding': outstanding,
        'flagged': flagged,
        'approved': approved,
        'rejected': rejected,
        'data': data,
    }
    return TemplateResponse(request, "fieldsight/project_dashboard.html", dashboard_data)

@login_required
def site_dashboard(request, pk):
    obj = Site.objects.get(pk=pk)
    peoples_involved = UserRole.objects.filter(site=obj).distinct('user')
    data = serialize('geojson', [obj], geometry_field='location',
                     fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone',))

    outstanding, flagged, approved, rejected = Submission.get_site_submission(pk)
    dashboard_data = {
        'obj': obj,
        'peoples_involved': peoples_involved,
        'outstanding': outstanding,
        'flagged': flagged,
        'approved': approved,
        'rejected': rejected,
        'data': data,
    }
    return TemplateResponse(request, "fieldsight/site_dashboard.html", dashboard_data)


class OrganizationView(object):
    model = Organization
    success_url = reverse_lazy('fieldsight:organizations-list')
    form_class = OrganizationForm


class UserDetailView(object):
    model = User
    success_url = reverse_lazy('fieldsight:user-list')
    form_class = RegistrationForm


class OrganizationListView(OrganizationView, LoginRequiredMixin, SuperAdminMixin, ListView):
    pass


class OrganizationCreateView(OrganizationView, LoginRequiredMixin, SuperAdminMixin, CreateView):
    pass


class OrganizationUpdateView(OrganizationView, LoginRequiredMixin, SuperAdminMixin, UpdateView):
    pass


class OrganizationDeleteView(OrganizationView,LoginRequiredMixin, SuperAdminMixin, DeleteView):
    pass

@login_required
@group_required('admin')
def alter_org_status(request, pk):
    try:
        obj = Organization.objects.get(pk=int(pk))
            # alter status method on custom user
        if obj.is_active:
            obj.is_active = False
            messages.info(request, 'Organization {0} Deactivated.'.format(obj.name))
        else:
            obj.is_active = True
            messages.info(request, 'Organization {0} Activated.'.format(obj.name))
        obj.save()
    except:
        messages.info(request, 'Organization {0} not found.'.format(obj.name))
    return HttpResponseRedirect(reverse('fieldsight:organizations-list'))


@login_required
@group_required('admin')
def add_org_admin_old(request, pk):
    obj = get_object_or_404(
        Organization, id=pk)
    if request.method == 'POST':
        form = SetOrgAdminForm(request.POST)
        user = int(form.data.get('user'))
        group = Group.objects.get(name__exact="Organization Admin")
        role = UserRole(user_id=user, group=group, organization=obj)
        role.save()
        messages.add_message(request, messages.INFO, 'Organization Admin Added')
        return HttpResponseRedirect(reverse('fieldsight:organizations-list'))
    else:
        form = SetOrgAdminForm(instance=obj)
    return render(request, "fieldsight/add_admin.html", {'obj':obj,'form':form})


@login_required
@group_required('Organization')
def add_org_admin(request, pk=None):
    organization = get_object_or_404(Organization, id=pk)
    group = Group.objects.get(name__exact="Organization Admin")
    role_obj = UserRole(organization=organization,group=group)
    scenario = 'Assign'
    if request.POST:
        form = AssignOrgAdmin(data=request.POST, instance=role_obj, request=request)
        if form.is_valid():
            role_obj = form.save(commit=False)
            user_id = request.POST.get('user')
            role_obj.user_id = int(user_id)
            role_obj.save()
            messages.add_message(request, messages.INFO, 'Organization Admin Added')
            return HttpResponseRedirect(reverse("fieldsight:organization-dashboard", kwargs={'pk': pk}))
    else:
        form = AssignOrgAdmin(instance=role_obj, request=request)
    return render(request, 'fieldsight/add_admin_form.html',
                  {'form': form, 'scenario': scenario, 'obj': organization})


@login_required
@group_required('Organization')
def alter_proj_status(request, pk):
    try:
        obj = Project.objects.get(pk=int(pk))
            # alter status method on custom user
        if obj.is_active:
            obj.is_active = False
            messages.info(request, 'Project {0} Deactivated.'.format(obj.name))
        else:
            obj.is_active = True
            messages.info(request, 'Project {0} Activated.'.format(obj.name))
        obj.save()
    except:
        messages.info(request, 'Project {0} not found.'.format(obj.name))
    return HttpResponseRedirect(reverse('fieldsight:projects-list'))


@login_required
@group_required('Project')
def add_proj_manager(request, pk):
    obj = get_object_or_404(
        Project, pk=pk)
    group = Group.objects.get(name__exact="Project Manager")
    role_obj = UserRole(project=obj, group=group)
    scenario = 'Assign'
    if request.method == 'POST':
        form = SetProjectManagerForm(data=request.POST, instance=role_obj, request=request)
        if form.is_valid():
            role_obj = form.save(commit=False)
            user_id = request.POST.get('user')
            role_obj.user_id = int(user_id)
            role_obj.save()
        messages.add_message(request, messages.INFO, 'Project Manager Added')
        return HttpResponseRedirect(reverse("fieldsight:project-dashboard", kwargs={'pk': obj.pk}))
    else:
        form = SetProjectManagerForm(instance=role_obj, request=request)
    return render(request, "fieldsight/add_project_manager.html", {'obj':obj,'form':form, 'scenario':scenario})


@login_required
@group_required('Project')
def alter_site_status(request, pk):
    try:
        obj = Site.objects.get(pk=int(pk))
        if obj.is_active:
            obj.is_active = False
            messages.info(request, 'Site {0} Deactivated.'.format(obj.name))
        else:
            obj.is_active = True
            messages.info(request, 'Site {0} Activated.'.format(obj.name))
        obj.save()
    except:
        messages.info(request, 'Site {0} not found.'.format(obj.name))
    return HttpResponseRedirect(reverse('fieldsight:sites-list'))


@login_required
@group_required('Project')
def add_supervisor(request, pk):
    obj = get_object_or_404(
        Site, pk=int(pk))
    group = Group.objects.get(name__exact="Site Supervisor")
    role_obj = UserRole(site=obj, group=group)
    if request.method == 'POST':
        form = SetSupervisorForm(data=request.POST, instance=role_obj, request=request)
        if form.is_valid():
            role_obj = form.save(commit=False)
            user_id = request.POST.get('user')
            role_obj.user_id = int(user_id)
            role_obj.save()
        messages.add_message(request, messages.INFO, 'Site Supervisor Added')
        return HttpResponseRedirect(reverse("fieldsight:site-dashboard", kwargs={'pk': obj.pk}))
    else:
        form = SetSupervisorForm(instance=role_obj, request=request)
    return render(request, "fieldsight/add_supervisor.html", {'obj':obj,'form':form})


@login_required
@group_required('Project')
def add_central_engineer(request, pk):
    obj = get_object_or_404(
        Project, pk=pk)
    group = Group.objects.get(name__exact="Central Engineer")
    role_obj = UserRole(project=obj, group=group)
    scenario = 'Assign'
    if request.method == 'POST':
        form = SetCentralEngForm(data=request.POST, instance=role_obj, request=request)
        if form.is_valid():
            role_obj = form.save(commit=False)
            user_id = request.POST.get('user')
            role_obj.user_id = int(user_id)
            role_obj.save()
        messages.add_message(request, messages.INFO, 'Central Engineer Added')
        return HttpResponseRedirect(reverse("fieldsight:project-dashboard", kwargs={'pk': obj.pk}))
    else:
        form = SetCentralEngForm(instance=role_obj, request=request)
    return render(request, "fieldsight/add_central_engineer.html", {'obj':obj,'form':form, 'scenario':scenario})


class ProjectView(OView):
    model = Project
    success_url = reverse_lazy('fieldsight:project-list')
    form_class = ProjectForm


class ProjectListView(ProjectView, OrganizationMixin, ListView):
    pass


class ProjectCreateView(ProjectView, OrganizationMixin, CreateView):
    pass


class ProjectUpdateView(ProjectView, OrganizationMixin, UpdateView):
    pass


class ProjectDeleteView(ProjectView, OrganizationMixin, DeleteView):
    pass


class SiteView(PView):
    model = Site
    success_url = reverse_lazy('fieldsight:sites-list')
    form_class = SiteForm


class SiteListView(SiteView, ProjectMixin, ListView):
    pass


class SiteCreateView(SiteView, ProjectMixin, CreateView):
    pass


class SiteUpdateView(SiteView, ProjectMixin, UpdateView):
    pass


class SiteDeleteView(SiteView, ProjectMixin, DeleteView):
    pass


class UserListView(ProjectMixin, OrganizationViewFromProfile, ListView):
    def get_template_names(self):
        return ['fieldsight/user_list.html']

    # def get_queryset(self):
    #     return User.objects.filter(pk__gt=0)


class CreateUserView(LoginRequiredMixin, ProjectMixin, UserDetailView, RegistrationView):
    def register(self, request, form, *args, **kwargs):
        with transaction.atomic():
            new_user = super(CreateUserView, self).register(
                request, form, *args, **kwargs)
            is_active = form.cleaned_data['is_active']
            new_user.first_name = request.POST.get('name', '')
            new_user.is_active = is_active
            new_user.save()
            try:
                org = request.organization
                if not org:
                    org = org.id
            except:
                organization = int(form.cleaned_data['organization'])
                org = Organization.objects.get(pk=organization)
                user_profile, created = UserProfile.objects.get_or_create(user=new_user, organization=org)

            else:
                user_profile, created = UserProfile.objects.get_or_create(user=new_user, organization=org)

        return new_user

