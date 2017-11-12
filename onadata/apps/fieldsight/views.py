import json
from django.http import HttpResponse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.response import TemplateResponse
from django.views.generic import ListView, TemplateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.forms.forms import NON_FIELD_ERRORS
from django.http import HttpResponse

from fcm.utils import get_device_model

import django_excel as excel
from registration.backends.default.views import RegistrationView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from channels import Group as ChannelGroup

from onadata.apps.eventlog.models import FieldSightLog
from onadata.apps.fieldsight.bar_data_project import BarGenerator
from onadata.apps.fsforms.Submission import Submission
from onadata.apps.fsforms.line_data_project import LineChartGenerator, LineChartGeneratorOrganization, \
    LineChartGeneratorSite
from onadata.apps.fsforms.models import FieldSightXF, Stage, FInstance
from onadata.apps.userrole.models import UserRole
from onadata.apps.users.models import UserProfile
from .mixins import (LoginRequiredMixin, SuperAdminMixin, OrganizationMixin, ProjectMixin, SiteView,
                     CreateView, UpdateView, DeleteView, OrganizationView as OView, ProjectView as PView,
                     group_required, OrganizationViewFromProfile, ReviewerMixin, MyOwnOrganizationMixin,
                     MyOwnProjectMixin, ProjectMixin)
from .rolemixins import SiteSupervisorRoleMixin, ProjectRoleView, ReviewerRoleMixin, ProjectRoleMixin, OrganizationRoleMixin, ReviewerRoleMixinDeleteView, ProjectRoleMixinDeleteView
from .models import Organization, Project, Site, ExtraUserDetail, BluePrints, UserInvite
from .forms import (OrganizationForm, ProjectForm, SiteForm, RegistrationForm, SetProjectManagerForm, SetSupervisorForm,
                    SetProjectRoleForm, AssignOrgAdmin, UploadFileForm, BluePrintForm, ProjectFormKo)
from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, smart_str
from django.utils.crypto import get_random_string
from django.http import HttpResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.db.models import Prefetch
from django.core.files.storage import FileSystemStorage
import pyexcel as p
from onadata.apps.fieldsight.tasks import multiuserassignproject, bulkuploadsites, multiuserassignsite

@login_required
def dashboard(request):
    current_role_count = request.roles.count()
    if current_role_count == 1:
        current_role = request.roles[0]
        role_type = request.roles[0].group.name
        if role_type == "Site Supervisor":
            return HttpResponseRedirect(reverse("fieldsight:site-dashboard", kwargs={'pk': current_role.site.pk}))
        if role_type == "Reviewer":
            return HttpResponseRedirect(reverse("fieldsight:site-dashboard", kwargs={'pk': current_role.site.pk}))
        if role_type == "Project Manager":
            return HttpResponseRedirect(reverse("fieldsight:project-dashboard", kwargs={'pk': current_role.project.pk}))
        if role_type == "Organization Admin":
            return HttpResponseRedirect(reverse("fieldsight:organizations-dashboard",
                                                kwargs={'pk': current_role.organization.pk}))
    if current_role_count > 1:
        return HttpResponseRedirect(reverse("fieldsight:roles-dashboard"))

    total_users = User.objects.all().count()
    total_organizations = Organization.objects.all().count()
    total_projects = Project.objects.all().count()
    total_sites = Site.objects.all().count()
    data = serialize('custom_geojson', Site.objects.prefetch_related('site_instances').filter(is_survey=False, is_active=True), geometry_field='location', fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone','id'))
   
   
    # outstanding_query = FInstance.objects.filter(form_status=0)
    # data = serialize('custom_geojson', Site.objects.filter(is_survey=False, is_active=True).prefetch_related(Prefetch('site_instances', queryset=outstanding_query, to_attr='outstanding')), geometry_field='location', fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone','id'))
    # fs_forms = FieldSightXF.objects.all()
    # fs_forms = list(fs_forms)
    # # outstanding = flagged = approved = rejected = 0
    # for form in fs_forms:
    #     if form.form_status == 0:
    #         outstanding += 1
    #     elif form.form_status == 1:
    #         flagged +=1
    #     elif form.form_status == 2:
    #         approved +=1
    #     else:
    #         rejected +=1

    dashboard_data = {
        'total_users': total_users,
        'total_organizations': total_organizations,
        'total_projects': total_projects,
        'total_sites': total_sites,
        # 'outstanding': outstanding,
        # 'flagged': flagged,
        # 'approved': approved,
        # 'rejected': rejected,
        'data': data,
    }
    return TemplateResponse(request, "fieldsight/fieldsight_dashboard.html", dashboard_data)


def get_site_images(site_id):
    query = {'fs_site': str(site_id), '_deleted_at': {'$exists': False}}
    return settings.MONGO_DB.instances.find(query).sort([("_id", 1)]).limit(20)


def site_images(request, pk):
    cursor = get_site_images(pk)
    cursor = list(cursor)
    medias = []
    for index, doc in enumerate(cursor):
        for media in cursor[index].get('_attachments', []):
            if media:
                medias.append(media.get('download_url', ''))

    return JsonResponse({'images':medias[:5]})

class Organization_dashboard(LoginRequiredMixin, OrganizationRoleMixin, TemplateView):
    template_name = "fieldsight/organization_dashboard.html"
    def get_context_data(self, **kwargs):
        dashboard_data = super(Organization_dashboard, self).get_context_data(**kwargs)
        obj = Organization.objects.get(pk=self.kwargs.get('pk'))
        peoples_involved = obj.organization_roles.filter(ended_at__isnull=True).distinct('user_id')
        sites = Site.objects.filter(project__organization=obj,is_survey=False, is_active=True)
        data = serialize('custom_geojson', sites, geometry_field='location',
                         fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone', 'id'))
        projects = Project.objects.filter(organization=obj)
        total_projects = projects.count()
        total_sites = sites.count()
        outstanding, flagged, approved, rejected = obj.get_submissions_count()
        bar_graph = BarGenerator(sites)
        line_chart = LineChartGeneratorOrganization(obj)
        line_chart_data = line_chart.data()
        user = User.objects.filter(pk=self.kwargs.get('pk'))
        roles_org = UserRole.objects.filter(organization_id = self.kwargs.get('pk'), project__isnull = True, site__isnull = True, ended_at__isnull=True)

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
            'cumulative_data': line_chart_data.values(),
            'cumulative_labels': line_chart_data.keys(),
            'progress_data': bar_graph.data.values(),
            'progress_labels': bar_graph.data.keys(),
            'roles_org': roles_org,

        }
        return dashboard_data

class Project_dashboard(ProjectRoleMixin, TemplateView):
    template_name = "fieldsight/project_dashboard.html"
    
    def get_context_data(self, **kwargs):
        dashboard_data = super(Project_dashboard, self).get_context_data(**kwargs)
        obj = Project.objects.get(pk=self.kwargs.get('pk'))

        peoples_involved = obj.project_roles.filter(ended_at__isnull=True).distinct('user')

        sites = obj.sites.filter(is_active=True, is_survey=False)
        data = serialize('custom_geojson', sites, geometry_field='location',
                         fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone','id',))

        total_sites = sites.count()
        total_survey_sites = obj.sites.filter(is_survey=True).count()
        outstanding, flagged, approved, rejected = obj.get_submissions_count()
        bar_graph = BarGenerator(sites)
        line_chart = LineChartGenerator(obj)
        line_chart_data = line_chart.data()
        roles_project = UserRole.objects.filter(organization__isnull = False, project_id = self.kwargs.get('pk'), site__isnull = True, ended_at__isnull=True)


        dashboard_data = {
            'sites': sites,
            'obj': obj,
            'peoples_involved': peoples_involved,
            'total_sites': total_sites,
            'total_survey_sites': total_survey_sites,
            'outstanding': outstanding,
            'flagged': flagged,
            'approved': approved,
            'rejected': rejected,
            'data': data,
            'cumulative_data': line_chart_data.values(),
            'cumulative_labels': line_chart_data.keys(),
            'progress_data': bar_graph.data.values(),
            'progress_labels': bar_graph.data.keys(),
            'roles_project': roles_project,
    }
        return dashboard_data


class SiteSurveyListView(LoginRequiredMixin, ProjectMixin, TemplateView):
    def get(self, request, pk):
        return TemplateResponse(request, "fieldsight/site_survey_list.html", {'project':pk})


class SiteDashboardView(ReviewerRoleMixin, TemplateView):
    template_name = 'fieldsight/site_dashboard.html'

    def get_context_data(self, **kwargs):
        dashboard_data = super(SiteDashboardView, self).get_context_data(**kwargs)
        obj = Site.objects.get(pk=self.kwargs.get('pk'))
        peoples_involved = obj.site_roles.filter(ended_at__isnull=True).distinct('user')
        data = serialize('custom_geojson', [obj], geometry_field='location',
                         fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone', 'id'))

        line_chart = LineChartGeneratorSite(obj)
        line_chart_data = line_chart.data()

        outstanding, flagged, approved, rejected = obj.get_site_submission()
        dashboard_data = {
            'obj': obj,
            'peoples_involved': peoples_involved,
            'outstanding': outstanding,
            'flagged': flagged,
            'approved': approved,
            'rejected': rejected,
            'data': data,
            'cumulative_data': line_chart_data.values(),
            'cumulative_labels': line_chart_data.keys(),
        }
        return dashboard_data

class SiteSupervisorDashboardView(SiteSupervisorRoleMixin, TemplateView):
    template_name = 'fieldsight/site_supervisor_dashboard.html'

    def get_context_data(self, **kwargs):
        dashboard_data = super(SiteSupervisorDashboardView, self).get_context_data(**kwargs)
        obj = Site.objects.get(pk=self.kwargs.get('pk'))
        peoples_involved = obj.site_roles.all().order_by('user__first_name')
        data = serialize('custom_geojson', [obj], geometry_field='location',
                         fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone', 'id'))

        line_chart = LineChartGeneratorSite(obj)
        line_chart_data = line_chart.data()

        outstanding, flagged, approved, rejected = obj.get_site_submission()
        dashboard_data = {
            'obj': obj,
            'peoples_involved': peoples_involved,
            'outstanding': outstanding,
            'flagged': flagged,
            'approved': approved,
            'rejected': rejected,
            'data': data,
            'cumulative_data': line_chart_data.values(),
            'cumulative_labels': line_chart_data.keys(),
        }
        return dashboard_data

class OrganizationView(object):
    model = Organization
    success_url = reverse_lazy('fieldsight:organizations-list')
    form_class = OrganizationForm


class UserDetailView(object):
    model = User
    success_url = reverse_lazy('users:users')
    form_class = RegistrationForm


class OrganizationListView(OrganizationView, LoginRequiredMixin, SuperAdminMixin, ListView):
    pass


class OrganizationCreateView(OrganizationView, LoginRequiredMixin, SuperAdminMixin, CreateView):
    def form_valid(self, form):
        self.object = form.save()
        noti = self.object.logs.create(source=self.request.user, type=9, title="new Organization",
                                       organization=self.object, content_object=self.object,
                                       description="{0} created a new organization named {1}".
                                       format(self.request.user, self.object.name))
        result = {}
        result['description'] = '{0} created a new organization named {1} '.format(noti.source.get_full_name(), self.object.name)
        result['url'] = noti.get_absolute_url()
        # ChannelGroup("notify-{}".format(self.object.id)).send({"text": json.dumps(result)})
        ChannelGroup("notify-0").send({"text": json.dumps(result)})

        return HttpResponseRedirect(self.get_success_url())


class OrganizationUpdateView(OrganizationView, OrganizationRoleMixin, UpdateView):
    def get_success_url(self):
        return reverse('fieldsight:organizations-dashboard', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        self.object = form.save()
        noti = self.object.logs.create(source=self.request.user, type=13, title="edit Organization",
                                       organization=self.object, content_object=self.object,
                                       description="{0} changed the details of organization named {1}".
                                       format(self.request.user.get_full_name(), self.object.name))
        result = {}
        result['description'] = noti.description
        result['url'] = noti.get_absolute_url()
        ChannelGroup("notify-{0}".format(self.object.id)).send({"text": json.dumps(result)})
        ChannelGroup("notify-0").send({"text": json.dumps(result)})

        return HttpResponseRedirect(self.get_success_url())



class OrganizationDeleteView(OrganizationView, LoginRequiredMixin, SuperAdminMixin, DeleteView):
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

#
# @login_required
# @group_required('admin')
# def add_org_admin_old(request, pk):
#     obj = get_object_or_404(
#         Organization, id=pk)
#     if request.method == 'POST':
#         form = SetOrgAdminForm(request.POST)
#         user = int(form.data.get('user'))
#         group = Group.objects.get(name__exact="Organization Admin")
#         role = UserRole(user_id=user, group=group, organization=obj)
#         role.save()
#         messages.add_message(request, messages.INFO, 'Organization Admin Added')
#         return HttpResponseRedirect(reverse('fieldsight:organizations-list'))
#     else:
#         form = SetOrgAdminForm(instance=obj)
#     return render(request, "fieldsight/add_admin.html", {'obj':obj,'form':form})

class OrganizationadminCreateView(LoginRequiredMixin, OrganizationRoleMixin, TemplateView):

    def get(self, request, pk=None):
        organization = get_object_or_404(Organization, id=pk)
        form = AssignOrgAdmin(request=request)
        scenario = 'Assign'
        return render(request, 'fieldsight/add_admin_form.html',
                      {'form': form, 'scenario': scenario, 'obj': organization})

    def post(self, request):
        organization = get_object_or_404(Organization, id=id)
        group = Group.objects.get(name__exact="Organization Admin")
        role_obj = UserRole(organization=organization, group=group)
        form = AssignOrgAdmin(data=request.POST, instance=role_obj, request=request)
        if form.is_valid():
            role_obj = form.save(commit=False)
            user_id = request.POST.get('user')
            role_obj.user_id = int(user_id)
            role_obj.save()
            messages.add_message(request, messages.INFO, 'Organization Admin Added')
            return HttpResponseRedirect(reverse("fieldsight:organizations-dashboard", kwargs={'pk': id}))


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


@group_required('Project')
def stages_status_download(request, pk):
    try:
        data = []
        ss_index = {}
        stages_rows = []
        head_row = ["Site ID", "Name", "Address", "Latitude", "longitude", "Status"]
        project = Project.objects.get(pk=pk)
        stages = project.stages.filter(stage__isnull=True)
        for stage in stages:
            sub_stages = stage.parent.all()
            if len(sub_stages):
                head_row.append("Stage :"+stage.name)
                stages_rows.append("Stage :"+stage.name)

                for ss in sub_stages:
                    head_row.append("Sub Stage :"+ss.name)
                    ss_index.update({head_row.index("Sub Stage :"+ss.name): ss.id})
        data.append(head_row)
        total_cols = len(head_row) - 6 # for non stages
        for site in project.sites.filter(is_active=True, is_survey=False):
            site_row = [site.identifier, site.name, site.address, site.latitude, site.longitude, site.status]
            site_row.extend([None]*total_cols)
            for k, v in ss_index.items():
                if Stage.objects.filter(project_stage_id=v, site=site).count() == 1:
                    site_sub_stage = Stage.objects.get(project_stage_id=v, site=site)
                    site_row[k] = site_sub_stage.form_status
            data.append(site_row)

        p.save_as(array=data, dest_file_name="media/stage-report/{}_stage_data.xls".format(project.id))
        xl_data = open("media/stage-report/{}_stage_data.xls".format(project.id), "rb")
        response = HttpResponse(xl_data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="report.xls"'
        return response
    except Exception as e:
        messages.info(request, 'Data Creattion Failed {}'.format(str(e)))
    return HttpResponse("failed Data Creattion Failed {}".format(str(e)))


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
@group_required('Reviewer')
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
    group = Group.objects.get(name__exact="Reivewer")
    role_obj = UserRole(project=obj, group=group)
    scenario = 'Assign'
    if request.method == 'POST':
        form = SetProjectRoleForm(data=request.POST, instance=role_obj, request=request)
        if form.is_valid():
            role_obj = form.save(commit=False)
            user_id = request.POST.get('user')
            role_obj.user_id = int(user_id)
            role_obj.save()
        messages.add_message(request, messages.INFO, 'Reviewer Added')
        return HttpResponseRedirect(reverse("fieldsight:project-dashboard", kwargs={'pk': obj.pk}))
    else:
        form = SetProjectRoleForm(instance=role_obj, request=request,)
    return render(request, "fieldsight/add_central_engineer.html", {'obj':obj,'form':form, 'scenario':scenario})


@login_required
@group_required('Project')
def add_project_role(request, pk):
    obj = get_object_or_404(
        Project, pk=pk)
    role_obj = UserRole(project=obj)
    scenario = 'Assign People'
    form = SetProjectRoleForm(instance=role_obj, request=request)
    if request.method == 'POST':
        form = SetProjectRoleForm(data=request.POST, instance=role_obj, request=request)
        if form.is_valid():
            role_obj = form.save(commit=False)
            user_id = request.POST.get('user')
            role_obj.user_id = int(user_id)
            role_obj.save()
            messages.add_message(request, messages.INFO, '{} Added'.format(role_obj.group.name))
            return HttpResponseRedirect(reverse("fieldsight:project-dashboard", kwargs={'pk': obj.pk}))
    existing_staffs = obj.get_staffs
    return render(request, "fieldsight/add_central_engineer.html", {'obj':obj,'form':form, 'scenario':scenario,
                                                                    "existing_staffs":existing_staffs})


class ProjectView(object):
    model = Project
    success_url = reverse_lazy('fieldsight:project-list')
    form_class = ProjectForm

class ProjectRoleView(object):
    model = Project
    success_url = reverse_lazy('fieldsight:project-list')
    form_class = ProjectForm

class ProjectListView(ProjectRoleView, OrganizationMixin, ListView):
    pass
    


class ProjectCreateView(ProjectView, OrganizationRoleMixin, CreateView):

    def form_valid(self, form):
        self.object = form.save(organization_id=self.kwargs.get('pk'), new=True)
        
        noti = self.object.logs.create(source=self.request.user, type=10, title="new Project",
                                       organization=self.object.organization, content_object=self.object,
                                       description='{0} created new project named {1}'.format(
                                           self.request.user.get_full_name(), self.object.name))
        result = {}
        result['description'] = noti.description
        result['url'] = noti.get_absolute_url()
        ChannelGroup("notify-{}".format(self.object.organization.id)).send({"text": json.dumps(result)})
        # ChannelGroup("notify-0").send({"text": json.dumps(result)})


        return HttpResponseRedirect(self.object.get_absolute_url())


class ProjectUpdateView(ProjectView, ProjectRoleMixin, UpdateView):
    def get_success_url(self):
        return reverse('fieldsight:project-dashboard', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        self.object = form.save(new=False)
        noti = self.object.logs.create(source=self.request.user, type=14, title="Edit Project",
                                       organization=self.object.organization,
                                       project=self.object, content_object=self.object,
                                       description='{0} changed the details of project named {1}'.format(
                                           self.request.user.get_full_name(), self.object.name))
        result = {}
        result['description'] = noti.description
        result['url'] = noti.get_absolute_url()
        ChannelGroup("notify-{}".format(self.object.organization.id)).send({"text": json.dumps(result)})
        ChannelGroup("project-{}".format(self.object.id)).send({"text": json.dumps(result)})

        return HttpResponseRedirect(self.get_success_url())



class ProjectDeleteView(ProjectView, ProjectRoleMixinDeleteView, DeleteView):
    def get_success_url(self):
        return reverse('fieldsight:org-project-list', kwargs={'pk': self.kwargs['org_id'] })

    def delete(self,*args, **kwargs):
        self.kwargs['org_id'] = self.get_object().organization_id
        self.object = self.get_object().delete()
        # noti = self.object.logs.create(source=self.request.user, type=4, title="new Site",
        #                                organization=self.object.organization,
        #                                description="new project {0} deleted by {1}".
        #                                format(self.object.name, self.request.user.username))
        # result = {}
        # result['description'] = 'new project {0} deleted by {1}'.format(self.object.name, self.request.user.username)
        # result['url'] = noti.get_absolute_url()
        # ChannelGroup("notify-{}".format(self.object.organization.id)).send({"text": json.dumps(result)})
        # ChannelGroup("notify-0").send({"text": json.dumps(result)})
        return HttpResponseRedirect(self.get_success_url())



class SiteView(PView):
    model = Site
    # success_url = reverse_lazy('fieldsight:org-site-list')
    form_class = SiteForm


class SiteListView(SiteView, ReviewerRoleMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super(SiteListView, self).get_context_data(**kwargs)
        context['form'] = SiteForm()
        return context


class SiteCreateView(SiteView, ProjectRoleMixin, CreateView):

    def get_success_url(self):
        return reverse('fieldsight:site-dashboard', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        self.object = form.save(project_id=self.kwargs.get('pk'), new=True)
        noti = self.object.logs.create(source=self.request.user, type=11, title="new Site",
                                       organization=self.object.project.organization,
                                       project=self.object.project, content_object=self.object, extra_object=self.object.project,
                                       description='{0} created a new site named {1} in {2}'.format(self.request.user.get_full_name(),
                                                                                 self.object.name, self.object.project.name))
        result = {}
        result['description'] = '{0} created a new site named {1} in {2}'.format(self.request.user.get_full_name(),
                                                                                 self.object.name, self.object.project.name)
        result['url'] = noti.get_absolute_url()
        ChannelGroup("project-{}".format(self.object.project.id)).send({"text": json.dumps(result)})
        # ChannelGroup("notify-0").send({"text": json.dumps(result)})

        return HttpResponseRedirect(self.get_success_url())



class SiteUpdateView(SiteView, ReviewerRoleMixin, UpdateView):
    def get_success_url(self):
        return reverse('fieldsight:site-dashboard', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        self.object = form.save(project_id=self.kwargs.get('pk'), new=False)
        noti = self.object.logs.create(source=self.request.user, type=15, title="edit Site",
                                       organization=self.object.project.organization, project=self.object.project, content_object=self.object,
                                       description='{0} changed the details of site named {1}'.format(
                                           self.request.user.get_full_name(), self.object.name))
        result = {}
        result['description'] = 'new site {0} updated by {1}'.format(self.object.name, self.request.user.username)
        result['url'] = noti.get_absolute_url()
        ChannelGroup("notify-{}".format(self.object.project.organization.id)).send({"text": json.dumps(result)})
        ChannelGroup("project-{}".format(self.object.project.id)).send({"text": json.dumps(result)})
        ChannelGroup("site-{}".format(self.object.id)).send({"text": json.dumps(result)})
        # ChannelGroup("notify-0").send({"text": json.dumps(result)})

        return HttpResponseRedirect(self.get_success_url())


class SiteDeleteView(SiteView, ProjectRoleMixin, DeleteView):
    def get_success_url(self):
        return reverse('fieldsight:proj-site-list', kwargs={'pk': self.object.project_id})

    # def delete(self,*args, **kwargs):
    #     self.kwargs['pk'] = self.get_object().pk
    #     self.object = self.get_object().delete()
    #     # noti = self.object.logs.create(source=self.request.user, type=4, title="new Site",
    #     #                                organization=self.object.organization,
    #     #                                description="new project {0} deleted by {1}".
    #     #                                format(self.object.name, self.request.user.username))
    #     # result = {}
    #     # result['description'] = 'new project {0} deleted by {1}'.format(self.object.name, self.request.user.username)
    #     # result['url'] = noti.get_absolute_url()
    #     # ChannelGroup("notify-{}".format(self.object.organization.id)).send({"text": json.dumps(result)})
    #     # ChannelGroup("notify-0").send({"text": json.dumps(result)})
    #     return HttpResponseRedirect(self.get_success_url())
    #


@group_required("Project")
@api_view(['POST'])
def ajax_upload_sites(request, pk):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        count = 0
        project = Project(pk=pk)
        try:
            sites = request.FILES['file'].get_records()
            count = len(sites)
            with transaction.atomic():
                for site in sites:
                    site = dict((k,v) for k,v in site.iteritems() if v is not '')
                    lat = site.get("longitude", 85.3240)
                    long = site.get("latitude", 27.7172)
                    location = Point(lat, long, srid=4326)
                    type_id = int(site.get("type", "1"))
                    _site, created = Site.objects.get_or_create(identifier=str(site.get("id")), name=site.get("name"),
                                                                project=project, type_id=type_id)
                    _site.phone = site.get("phone")
                    _site.address = site.get("address")
                    _site.public_desc = site.get("public_desc"),
                    _site.additional_desc = site.get("additional_desc")
                    _site.location=location
                    _site.save()
            if count:
                noti = project.logs.create(source=request.user, type=12, title="Bulk Sites",
                                       organization=project.organization,
                                       project=project, content_object=project,
                                       extra_message=count + "Sites",
                                       description='{0} created a {1} sites in {2}'.
                                           format(request.user.get_full_name(), count, project.name))
                result = {}
                result['description'] = noti.description
                result['url'] = noti.get_absolute_url()
                ChannelGroup("project-{}".format(project.id)).send({"text": json.dumps(result)})
            return Response({'msg': 'ok'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'file':e.message}, status=status.HTTP_400_BAD_REQUEST)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


@group_required("Project")
@api_view(['POST'])
def ajax_save_site(request):
    id = request.POST.get('id', False)
    if id =="undefined":
        id = False
    if id:
        instance = Site.objects.get(pk=id)
        form = SiteForm(request.POST, request.FILES, instance)
    else:
        form = SiteForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        return Response({'msg': 'ok'}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid Site Data'}, status=status.HTTP_400_BAD_REQUEST)


@group_required("Organization")
@api_view(['POST'])
def ajax_save_project(request):
    id = request.POST.get('id', False)
    if id =="undefined":
        id = False
    if id:
        instance = Project.objects.get(pk=id)
        form = ProjectFormKo(request.POST, request.FILES, instance)
    else:
        form = ProjectFormKo(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        return Response({'msg': 'ok'}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid Project Data'}, status=status.HTTP_400_BAD_REQUEST)

class UploadSitesView(ProjectRoleMixin, TemplateView):

    def get(self, request, pk):
        form = UploadFileForm()
        return render(request, 'fieldsight/upload_sites.html',{'form':form, 'project':pk})

    def post(self, request, pk=id):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                sitefile=request.FILES['file']
                # sites = request.FILES['file'].get_records()
                user = request.user
                bulkuploadsites.delay(user, sitefile, pk)
                # sites = request.FILES['file'].get_records()
                # with transaction.atomic():
                #     for site in sites:
                #         site = dict((k, v) for k, v in site.iteritems() if v is not '')
                #         lat = site.get("longitude", 85.3240)
                #         long = site.get("latitude", 27.7172)
                #         location = Point(lat, long, srid=4326)
                #         type_id = int(site.get("type", "1"))
                #         _site, created = Site.objects.get_or_create(identifier=str(site.get("id")),
                #                                                     name=site.get("name"),
                #                                                     project=project, type_id=type_id)
                #         _site.phone = site.get("phone")
                #         _site.address = site.get("address")
                #         _site.public_desc = site.get("public_desc"),
                #         _site.additional_desc = site.get("additional_desc")
                #         _site.location = location
                #         _site.save()
                # messages.info(request, 'Site Upload Succesfull')
                messages.success(request, 'Sites are being uploaded. You will be notified in notifications list as well.')
                return HttpResponseRedirect(reverse('fieldsight:proj-site-list', kwargs={'pk': pk}))
            except Exception as e:
                print e
                form.full_clean()
                form._errors[NON_FIELD_ERRORS] = form.error_class(['Sites Upload Failed, UnSupported Data', e])
                messages.warning(request, 'Site Upload Failed, UnSupported Data ')
        return render(request, 'fieldsight/upload_sites.html', {'form': form, 'project': pk})


def download(request):
    sheet = excel.pe.Sheet([[1, 2],[3, 4]])
    return excel.make_response(sheet, "csv")


class UserListView(ProjectMixin, OrganizationViewFromProfile, ListView):
    def get_template_names(self):
        return ['fieldsight/user_list.html']

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        return context


class FilterUserView(TemplateView):
    def get(self, *args, **kwargs):
        return redirect('fieldsight:user-list')

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        role = request.POST.get('role')
        groups = Group.objects.all()
        object_list = User.objects.filter(is_active=True, pk__gt=0)
        if name:
            object_list = object_list.filter(
                Q(first_name__contains=name) | Q(last_name__contains=name) | Q(username__contains=name))
        if role and role != '0':
            object_list = object_list.filter(user_roles__group__id=role)
        if hasattr(request, "organization") and request.organization:
            object_list = object_list.filter(user_roles__organization=request.organization)
        return render(request, 'fieldsight/user_list.html', {'object_list': object_list, 'groups': groups})



class CreateUserView(LoginRequiredMixin, SuperAdminMixin, UserDetailView, RegistrationView):
    def register(self, request, form, *args, **kwargs):
        with transaction.atomic():
            new_user = super(CreateUserView, self).register(
                request, form, *args, **kwargs)
            is_active = form.cleaned_data['is_active']
            new_user.first_name = request.POST.get('name', '')
            new_user.is_active = is_active
            new_user.is_superuser = True
            new_user.save()
            organization = int(form.cleaned_data['organization'])
            org = Organization.objects.get(pk=organization)
            profile = UserProfile(user=new_user, organization=org)
            profile.save()
            # noti = profile.logs.create(source=self.request.user, type=0, title="new User",
            #                         organization=profile.organization, description="new user {0} created by {1}".
            #                         format(new_user.username, self.request.user.username))
            # result = {}
            # result['description'] = 'new user {0} created by {1}'.format(new_user.username, self.request.user.username)
            # result['url'] = noti.get_absolute_url()
            # ChannelGroup("notify-{}".format(profile.organization.id)).send({"text":json.dumps(result)})
            # ChannelGroup("notify-0").send({"text":json.dumps(result)})

        return new_user

class BluePrintsView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        ImageFormSet = modelformset_factory(BluePrints, form=BluePrintForm, extra=5)
        formset = ImageFormSet(queryset=BluePrints.objects.none())
        return render(request, 'fieldsight/blueprints_form.html', {'formset': formset,'id': self.kwargs.get('id')},)

    def post(self, request, id):
        ImageFormSet = modelformset_factory(BluePrints, form=BluePrintForm, extra=5)
        formset = ImageFormSet(request.POST, request.FILES,
                                   queryset=BluePrints.objects.none())

        if formset.is_valid():
            for form in formset.cleaned_data:
                if 'image' in form:
                    image = form['image']
                    photo = BluePrints(site_id=id, image=image)
                    photo.save()
            messages.success(request,
                             "Blueprints saved!")
            return HttpResponseRedirect(reverse("fieldsight:site-dashboard", kwargs={'pk': id}))

        formset = ImageFormSet(queryset=BluePrints.objects.none())
        return render(request, 'fieldsight/blueprints_form.html', {'formset': formset, 'id': self.kwargs.get('id')}, )


class ManagePeopleSiteView(LoginRequiredMixin, ReviewerRoleMixin, TemplateView):
    def get(self, request, pk):
        project = Site.objects.get(pk=pk).project
        return render(request, 'fieldsight/manage_people_site.html', {'pk':pk, 'level': "0", 'category':"site", 'organization': project.organization.id, 'project':project.id, 'site':pk})


class ManagePeopleProjectView(LoginRequiredMixin, ProjectRoleMixin, TemplateView):
    def get(self, request, pk):
        organization = Project.objects.get(pk=pk).organization.id
        return render(request, "fieldsight/manage_people_site.html",
                      {'pk': pk, 'level': "1", 'category':"Project Manager", 'organization': organization, 'project': pk, 'type':'project'})


class ManagePeopleOrganizationView(LoginRequiredMixin, OrganizationRoleMixin, TemplateView):
    def get(self, request, pk):
        return render(request, 'fieldsight/manage_people_site.html', {'pk': pk, 'level': "2", 'category':"Organization Admin", 'organization': pk, 'type':'org'})


def all_notification(user,  message):
    ChannelGroup("%s" % user).send({
        "text": json.dumps({
            "msg": message
        })
    })

class RolesView(LoginRequiredMixin, TemplateView):
    template_name = "fieldsight/roles_dashboard.html"
    def get_context_data(self, **kwargs):
        context = super(RolesView, self).get_context_data(**kwargs)
        context['org_admin'] = self.request.roles.select_related('organization').filter(group__name="Organization Admin")
        context['proj_manager'] = self.request.roles.select_related('project').filter(group__name = "Project Manager")
        context['site_reviewer'] = self.request.roles.select_related('site').filter(group__name = "Reviewer")
        context['site_supervisor'] = self.request.roles.select_related('site').filter(group__name = "Site Supervisor")
        return context


class OrgProjectList(OrganizationRoleMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super(OrgProjectList, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context
    def get_queryset(self):
        queryset = Project.objects.filter(organization_id=self.kwargs.get('pk'))
        return queryset


class OrgSiteList(OrganizationRoleMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super(OrgSiteList, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        context['type'] = "org"
        return context
    def get_queryset(self):
        queryset = Site.objects.filter(project__organization_id=self.kwargs.get('pk'),is_survey=False, is_active=True)
        return queryset

class ProjSiteList(ProjectRoleMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super(ProjSiteList, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        context['type'] = "project"
        context['is_form_proj'] = True
        return context
    def get_queryset(self):
        queryset = Site.objects.filter(project_id=self.kwargs.get('pk'),is_survey=False, is_active=True)
        return queryset

class OrgUserList(OrganizationRoleMixin, ListView):
    template_name = "fieldsight/user_list_updated.html"
    def get_context_data(self, **kwargs):
        context = super(OrgUserList, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context
    def get_queryset(self):
        #queryset = UserRole.objects.select_related('User').filter(organization_id=self.kwargs.get('pk')).distinct('user_id')
        #queryset = User.objects.select_related('user_profile').filter(user_profile__organization_id=self.kwargs.get('pk'))
        
        queryset = UserRole.objects.select_related('user').filter(organization_id=self.kwargs.get('pk'), ended_at__isnull=True).distinct('user_id')
        return queryset

class ProjUserList(ProjectRoleMixin, ListView):
    template_name = "fieldsight/user_list_updated.html"
    def get_context_data(self, **kwargs):
        context = super(ProjUserList, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        context['type'] = "project"
        return context
    def get_queryset(self):
        queryset = UserRole.objects.select_related('user').filter(project_id=self.kwargs.get('pk'), ended_at__isnull=True).distinct('user_id')
        return queryset

class SiteUserList(ReviewerRoleMixin, ListView):
    template_name = "fieldsight/user_list_updated.html"
    def get_context_data(self, **kwargs):
        context = super(SiteUserList, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        context['type'] = "site"
        return context
    def get_queryset(self):
        queryset = UserRole.objects.select_related('user').filter(site_id=self.kwargs.get('pk'), ended_at__isnull=True).distinct('user_id')
    
        return queryset

@login_required()
def ajaxgetuser(request):
    user = User.objects.filter(email=request.POST.get('email'))
    html = render_to_string('fieldsight/ajax_temp/ajax_user.html', {'department': User.objects.filter(email=user)})
    return HttpResponse(html)

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

@login_required()
def senduserinvite(request):
    emails =request.POST.getlist('emails[]')
    group = Group.objects.get(name=request.POST.get('group'))

    organization_id = None
    project_id =None
    site_id =None

    if RepresentsInt(request.POST.get('organization_id')):
        organization_id = request.POST.get('organization_id')
    if RepresentsInt(request.POST.get('project_id')):
        project_id = request.POST.get('project_id')
    if RepresentsInt(request.POST.get('site_id')):
        site_id = request.POST.get('site_id')

    response=""

    for email in emails:
        user = User.objects.filter(email=email)
        userinvite = UserInvite.objects.filter(email=email, organization_id=organization_id, group=group, project_id=project_id,  site_id=site_id, is_used=False)

        if userinvite:
            response += 'Invite for '+ email + ' in ' + group.name +' role has already been sent.<br>'
            continue
        if user:
            userrole = UserRole.objects.filter(user=user[0], group=group, organization_id=organization_id, project_id=project_id, site_id=site_id).order_by('-id')
            
            if userrole:
                if userrole[0].ended_at==None:
                    response += email + ' already has the role for '+group.name+'.<br>' 
                    continue
            invite = UserInvite(email=email, by_user_id=request.user.id ,group=group, token=get_random_string(length=32), organization_id=organization_id, project_id=project_id, site_id=site_id)

            invite.save()
            # organization = Organization.objects.get(pk=1)
            # noti = invite.logs.create(source=user[0], type=9, title="new Role",
            #                                organization_id=request.POST.get('organization_id'),
            #                                description="{0} sent you an invite to join {1} as the {2}.".
            #                                format(request.user.username, organization.name, invite.group.name,))
            # result = {}
            # result['description'] = 'new site {0} deleted by {1}'.format(self.object.name, self.request.user.username)
            # result['url'] = noti.get_absolute_url()
            # ChannelGroup("notify-{}".format(self.object.project.organization.id)).send({"text": json.dumps(result)})
            # ChannelGroup("notify-0").send({"text": json.dumps(result)})

        else:
            invite = UserInvite(email=email, by_user_id=request.user.id, token=get_random_string(length=32), group=group, project_id=project_id, organization_id=organization_id,  site_id=site_id)
            invite.save()
        current_site = get_current_site(request)
        subject = 'Invitation for Role'
        message = render_to_string('fieldsight/email_sample.html',
        {
            'email': invite.email,
            'domain': current_site.domain,
            'invite_id': urlsafe_base64_encode(force_bytes(invite.pk)),
            'token': invite.token,
            'invite': invite,
            })
        email_to = (invite.email,)
        send_mail(subject, message, 'Field Sight', email_to,fail_silently=False)
        response += "Sucessfully invited "+ email +" for "+ group.name +" role.<br>"
        continue
    return HttpResponse(response)



@login_required()
def sendmultiroleuserinvite(request):
    data = json.loads(request.body)
    emails =data.get('emails')
    levels =data.get('levels')
    leveltype =data.get('leveltype')
    group = Group.objects.get(name=data.get('group'))

    response=""

    for level in levels:
        organization_id = None
        project_id =None
        site_id =None

        if leveltype == "project":
            project_id = level
            organization_id = Project.objects.get(pk=level).organization_id
            print organization_id
        
        elif leveltype == "site":
            site_id = level
            site = Site.objects.get(pk=site_id)

            project_id = site.project_id
            organization_id = site.project.organization_id

        

        for email in emails:
            user = User.objects.filter(email=email)
            userinvite = UserInvite.objects.filter(email=email, organization_id=organization_id, group=group, project_id=project_id,  site_id=site_id, is_used=False)
            
            if userinvite:
                response += 'Invite for '+ email + ' in ' + group.name +' role has already been sent.<br>'
                continue
            if user:
                userrole = UserRole.objects.filter(user=user[0], group=group, organization_id=organization_id, project_id=project_id, site_id=site_id).order_by('-id')
                
                if userrole:
                    if userrole[0].ended_at==None:
                        response += email + ' already has the role for '+group.name+'.<br>' 
                        continue
                invite, created = UserInvite.objects.get_or_create(email=email, by_user_id=request.user.id ,group=group, token=get_random_string(length=32), organization_id=organization_id, project_id=project_id, site_id=site_id)

                # noti = invite.logs.create(source=user[0], type=9, title="new Role",
                #                                organization_id=request.POST.get('organization_id'),
                #                                description="{0} sent you an invite to join {1} as the {2}.".
                #                                format(request.user.username, organization.name, invite.group.name,))
                # result = {}
                # result['description'] = 'new site {0} deleted by {1}'.format(self.object.name, self.request.user.username)
                # result['url'] = noti.get_absolute_url()
                # ChannelGroup("notify-{}".format(self.object.project.organization.id)).send({"text": json.dumps(result)})
                # ChannelGroup("notify-0").send({"text": json.dumps(result)})

            else:
                invite, created = UserInvite.objects.get_or_create(email=email, by_user_id=request.user.id, token=get_random_string(length=32), group=group, project_id=project_id, organization_id=organization_id,  site_id=site_id)
            current_site = get_current_site(request)
            subject = 'Invitation for Role'
            message = render_to_string('fieldsight/email_sample.html',
            {
                'email': invite.email,
                'domain': current_site.domain,
                'invite_id': urlsafe_base64_encode(force_bytes(invite.pk)),
                'token': invite.token,
                'invite': invite,
                })
            email_to = (invite.email,)
            send_mail(subject, message, 'Field Sight', email_to,fail_silently=False)
            response += "Sucessfully invited "+ email +" for "+ group.name +" role.<br>"
            continue
    return HttpResponse(response)


# def activate_role(request, invite_idb64, token):
#     try:
#         invite_id = force_text(urlsafe_base64_decode(invite_idb64))
#         invite = UserInvite.objects.filter(id=invite_id, token=token, is_used=False)
#     except (TypeError, ValueError, OverflowError, UserInvite.DoesNotExist):
#         invite = None
#     if invite:
#         user = User.objects.filter(email=invite[0].email)
#         if user:
#             userrole = UserRole(user=user[0], group=invite[0].group, organization=invite[0].organization, project=invite[0].project, site=invite[0].site)
#             userrole.save()
#             return HttpResponse("Sucess")
#         else:

#     return HttpResponse("Failed")
   
class ActivateRole(TemplateView):
    def dispatch(self, request, invite_idb64, token):
        invite_id = force_text(urlsafe_base64_decode(invite_idb64))
        invite = UserInvite.objects.filter(id=invite_id, token=token, is_used=False)
        if invite:
            return super(ActivateRole, self).dispatch(request, invite[0], invite_idb64, token)
        return HttpResponseRedirect(reverse('login'))

    def get(self, request, invite, invite_idb64, token):
        user = User.objects.filter(email=invite.email)
        if invite.is_used==True:
            return HttpResponseRedirect(reverse('login'))
        if user:
            return render(request, 'fieldsight/invite_action.html',{'invite':invite, 'is_used': False, 'status':'',})
        else:
            return render(request, 'fieldsight/invited_user_reg.html',{'invite':invite, 'is_used': False, 'status':'',})
        

    def post(self, request, invite, *args, **kwargs):
        user_exists = User.objects.filter(email=invite.email)
        if user_exists:
            user = user_exists[0] 
            if request.POST.get('response') == "accept":
                userrole = UserRole.objects.get_or_create(user=user, group=invite.group, organization=invite.organization, project=invite.project, site=invite.site)
            else:
                invite.is_declined = True
            invite.is_used = True
            invite.save()
        else:
            username = request.POST.get('username')
            for i in username:
                if i.isupper():
                    return render(request, 'fieldsight/invited_user_reg.html',{'invite':invite, 'is_used': False, 'status':'error-3', 'username':request.POST.get('username'), 'firstname':request.POST.get('firstname'), 'lastname':request.POST.get('lastname')})
                    break
                if not i.isalnum():
                    return render(request, 'fieldsight/invited_user_reg.html',{'invite':invite, 'is_used': False, 'status':'error-1', 'username':request.POST.get('username'), 'firstname':request.POST.get('firstname'), 'lastname':request.POST.get('lastname')})
                    break
            if User.objects.filter(username=request.POST.get('username')).exists():
                return render(request, 'fieldsight/invited_user_reg.html',{'invite':invite, 'is_used': False, 'status':'error-2', 'username':request.POST.get('username'), 'firstname':request.POST.get('firstname'), 'lastname':request.POST.get('lastname')})

            user = User(username=request.POST.get('username'), email=invite.email, first_name=request.POST.get('firstname'), last_name=request.POST.get('lastname'))
            user.set_password(request.POST.get('password1'))
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user, organization=invite.organization)
            userrole, created = UserRole.objects.get_or_create(user=user, group=invite.group, organization=invite.organization, project=invite.project, site=invite.site)
            invite.is_used = True
            invite.save()

        if invite.group.name == "Organization Admin":
            noti_type = 1
            content = invite.organization
        elif invite.group.name == "Project Manager":
            noti_type = 2
            content = invite.project
        elif invite.group.name == "Reviewer":
            noti_type = 3
            content = invite.site
        elif invite.group.name == "Site Supervisor":
            noti_type = 4
            content = invite.site
        
        noti = invite.logs.create(source=user, type=noti_type, title="new Role",
                                       organization=invite.organization, project=invite.project, site=invite.site, content_object=content, extra_object=invite.by_user,
                                       description="{0} was added as the {1} of {2} by {3}.".
                                       format(user.username, invite.group.name, content.name, invite.by_user ))
        # result = {}
        # result['description'] = 'new site {0} deleted by {1}'.format(self.object.name, self.request.user.username)
        # result['url'] = noti.get_absolute_url()
        # ChannelGroup("notify-{}".format(self.object.project.organization.id)).send({"text": json.dumps(result)})
        # ChannelGroup("notify-0").send({"text": json.dumps(result)})
        return HttpResponseRedirect(reverse('login'))
            
@login_required()
def checkemailforinvite(request):
    user = User.objects.select_related('user_profile').filter(email__icontains=request.POST.get('email'))
    if user:
        return render(request, 'fieldsight/invite_response.html', {'users': user,})
    else:
        return HttpResponse("No existing User found.<a href='#' onclick='sendnewuserinvite()'>send</a>")

def checkusernameexists(request):
    user = User.objects.get(username=request.POST.get('email'))
    if user:
        return render(request, 'fieldsight/invite_response.html', {'users': user,})
    else:
        return HttpResponse("No existing User found.<a href='#' onclick='sendnewuserinvite()'>send</a>")


class ProjectSummaryReport(TemplateView):
    def get(self, request, pk):
        obj = Project.objects.get(pk=self.kwargs.get('pk'))
        organization = Organization.objects.get(pk=obj.organization_id)
        peoples_involved = obj.project_roles.filter(group__name__in=["Project Manager", "Reviewer"]).distinct('user')
        project_managers = obj.project_roles.select_related('user').filter(group__name__in=["Project Manager"]).distinct('user')

        sites = obj.sites.filter(is_active=True, is_survey=False)
        data = serialize('custom_geojson', sites, geometry_field='location',
                         fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone','id',))

        total_sites = len(sites)
        total_survey_sites = obj.sites.filter(is_survey=True).count()
        outstanding, flagged, approved, rejected = obj.get_submissions_count()
        bar_graph = BarGenerator(sites)

        line_chart = LineChartGenerator(obj)
        line_chart_data = line_chart.data()
        dashboard_data = {
            'sites': sites,
            'obj': obj,
            'peoples_involved': peoples_involved,
            'total_sites': total_sites,
            'total_survey_sites': total_survey_sites,
            'outstanding': outstanding,
            'flagged': flagged,
            'approved': approved,
            'rejected': rejected,
            'data': data,
            'cumulative_data': line_chart_data.values(),
            'cumulative_labels': line_chart_data.keys(),
            'progress_data': bar_graph.data.values(),
            'progress_labels': bar_graph.data.keys(),
            'project_managers':project_managers,
            'organization': organization,
            'total_submissions': line_chart_data.values()[-1],
    
        }
        return render(request, 'fieldsight/site_individual_submission_report.html', dashboard_data)

class MultiUserAssignSiteView(ProjectRoleMixin, TemplateView):
    def get(self, request, pk):
        project_obj = Project.objects.get(pk=pk)
        return render(request, 'fieldsight/multi_user_assign.html',{'type': "site", 'pk':pk})

    def post(self, request, pk, *args, **kwargs):
        data = json.loads(self.request.body)
        sites = data.get('sites')
        users = data.get('users')
        group = Group.objects.get(name=data.get('group'))
        user = request.user
        multiuserassignsite.delay(user, pk, sites, users, group.id)
        return HttpResponse('sucess')

# class MultiUserAssignSiteView(ProjectRoleMixin, TemplateView):
#     def get(self, request, pk):
#         project_obj = Project.objects.get(pk=pk)
#         return render(request, 'fieldsight/multi_user_assign.html',{'type': "site", 'pk':pk})

#     def post(self, request, *args, **kwargs):
#         data = json.loads(self.request.body)
#         sites = data.get('sites')
#         users = data.get('users')
#         group = Group.objects.get(name=data.get('group'))
#         response = ""
#         for site_id in sites:
#             site = Site.objects.get(pk=site_id)
#             for user in users:
              
#                 role, created = UserRole.objects.get_or_create(user_id=user, site_id=site.id,
#                                                                project__id=site.project.id, organization__id=site.project.organization_id, group=group, ended_at=None)
#                 if created:
               
#                     # description = "{0} was assigned  as {1} in {2}".format(
#                     #     role.user.get_full_name(), role.lgroup.name, role.project)
#                     noti_type = 8

#                     # if data.get('group') == "Reviewer":
#                     #     noti_type =7
                    
#                     # noti = role.logs.create(source=role.user, type=noti_type, title=description,
#                     #                         description=description, content_type=site, extra_object=self.request.user,
#                     #                         site=role.site)
#                     # result = {}
#                     # result['description'] = description
#                     # result['url'] = noti.get_absolute_url()
#                     # ChannelGroup("notify-{}".format(role.organization.id)).send({"text": json.dumps(result)})
#                     # ChannelGroup("project-{}".format(role.project.id)).send({"text": json.dumps(result)})
#                     # ChannelGroup("site-{}".format(role.site.id)).send({"text": json.dumps(result)})
#                     # ChannelGroup("notify-0").send({"text": json.dumps(result)})

#                     # Device = get_device_model()
#                     # if Device.objects.filter(name=role.user.email).exists():
#                     #     message = {'notify_type':'Assign Site', 'site':{'name': site.name, 'id': site.id}}
#                     #     Device.objects.filter(name=role.user.email).send_message(message)
#                 else:
#                     response += "Already exists."
#         return HttpResponse(response)



class MultiUserAssignProjectView(OrganizationRoleMixin, TemplateView):
    def get(self, request, pk):
        org_obj = Organization.objects.get(pk=pk)
        return render(request, 'fieldsight/multi_user_assign.html',{'type': "project", 'pk':pk})

    def post(self, request, pk, *args, **kwargs):
        data = json.loads(self.request.body)
        projects = data.get('projects')
        users = data.get('users')
     

        group_id = Group.objects.get(name="Project Manager").id
        user = request.user
        print user
        multiuserassignproject.delay(user, pk, projects, users, group_id)
        return HttpResponse("Sucess")

#May need it
# class MultiUserAssignProjectView(OrganizationRoleMixin, TemplateView):
#     def get(self, request, pk):
#         org_obj = Organization.objects.get(pk=pk)
#         return render(request, 'fieldsight/multi_user_assign.html',{'type': "project", 'pk':pk})

#     def post(self, request, *args, **kwargs):
#         data = json.loads(self.request.body)
#         projects = data.get('projects')
#         users = data.get('users')
     

#         group = Group.objects.get(name="Project Manager")
#         for project_id in projects:
#             project = Project.objects.get(pk=project_id)
#             for user in users:
#                 role, created = UserRole.objects.get_or_create(user_id=user, project_id=project_id,
#                                                                organization__id=project.organization.id,
#                                                                project__id=project_id,
#                                                                group=group, ended_at=None)
#                 if created:
#                     description = "{0} was assigned  as Project Manager in {1}".format(
#                         role.user.get_full_name(), role.project)
#                     noti = role.logs.create(source=role.user, type=6, title=description, description=description,
#                      content_object=role.project, extra_object=self.request.user)
#                     result = {}
#                     result['description'] = description
#                     result['url'] = noti.get_absolute_url()
#                     ChannelGroup("notify-{}".format(role.organization.id)).send({"text": json.dumps(result)})
#                     ChannelGroup("project-{}".format(role.project.id)).send({"text": json.dumps(result)})
#                     ChannelGroup("notify-0").send({"text": json.dumps(result)})
#         return HttpResponse("Sucess")


def viewfullmap(request):
    data = serialize('full_detail_geojson',
                     Site.objects.prefetch_related('site_instances').filter(is_survey=False, is_active=True),
                     geometry_field='location',
                     fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone', 'id'))

    dashboard_data = {

        'data': data,
    }
    return render(request, 'fieldsight/map.html', dashboard_data)


class OrgFullmap(LoginRequiredMixin, OrganizationRoleMixin, TemplateView):
    template_name = "fieldsight/map.html"
    def get_context_data(self, **kwargs):
        obj = Organization.objects.get(pk=self.kwargs.get('pk'))
        sites = Site.objects.filter(project__organization=obj,is_survey=False, is_active=True)

        data = serialize('full_detail_geojson', sites, geometry_field='location',
               fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone', 'id'))
        dashboard_data = {
           'data': data,
        }
        return dashboard_data


class ProjFullmap(ProjectRoleMixin, TemplateView):
    template_name = "fieldsight/map.html"
    def get_context_data(self, **kwargs):
        obj = Project.objects.get(pk=self.kwargs.get('pk'))
        sites = obj.sites.filter(is_active=True, is_survey=False)
        data = serialize('full_detail_geojson', sites, geometry_field='location',
                         fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone', 'id',))
        dashboard_data = {
            'data': data,
        }
        return dashboard_data

class SiteFullmap(ReviewerRoleMixin, TemplateView):
    template_name = "fieldsight/map.html"

    def get_context_data(self, **kwargs):
        obj = Site.objects.get(pk=self.kwargs.get('pk'))
        data = serialize('full_detail_geojson', [obj], geometry_field='location',
                         fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone', 'id'))
        dashboard_data = {

            'data': data,
        }
        return dashboard_data


class OrganizationdataSubmissionView(TemplateView):
    template_name = "fieldsight/organizationdata_submission.html"

    def get_context_data(self, **kwargs):
        data = super(OrganizationdataSubmissionView, self).get_context_data(**kwargs)
        obj = Organization.objects.get(pk=self.kwargs.get('pk'))
        data['pending'] = FInstance.objects.filter(project__organization=self.kwargs.get('pk'), form_status='0')
        data['rejected'] = FInstance.objects.filter(project__organization=self.kwargs.get('pk'), form_status='1')
        data['flagged'] = FInstance.objects.filter(project__organization=self.kwargs.get('pk'), form_status='2')
        data['approved'] = FInstance.objects.filter(project__organization=self.kwargs.get('pk'), form_status='3')
        data['type'] = self.kwargs.get('type')

        return data


class ProjectdataSubmissionView(ProjectRoleMixin, TemplateView):
    template_name = "fieldsight/projectdata_submission.html"

    def get_context_data(self, **kwargs):
        data = super(ProjectdataSubmissionView, self).get_context_data(**kwargs)
        obj = Project.objects.get(pk=self.kwargs.get('pk'))
        data['pending'] = FInstance.objects.filter(project_id=self.kwargs.get('pk'), form_status='0')
        data['rejected'] = FInstance.objects.filter(project_id=self.kwargs.get('pk'), form_status='1')
        data['flagged'] = FInstance.objects.filter(project_id=self.kwargs.get('pk'), form_status='2')
        data['approved'] = FInstance.objects.filter(project_id=self.kwargs.get('pk'), form_status='3')
        data['type'] = self.kwargs.get('type')

        return data


class SitedataSubmissionView(TemplateView):
    template_name = "fieldsight/sitedata_submission.html"

    def get_context_data(self, **kwargs):
        data = super(SitedataSubmissionView, self).get_context_data(**kwargs)
        obj = Site.objects.get(pk=self.kwargs.get('pk'))
        data['pending'] = FInstance.objects.filter(site_id = self.kwargs.get('pk'), form_status = '0')
        data['rejected'] = FInstance.objects.filter(site_id = self.kwargs.get('pk'), form_status = '1')
        data['flagged'] = FInstance.objects.filter(site_id = self.kwargs.get('pk'), form_status = '2')
        data['approved'] = FInstance.objects.filter(site_id = self.kwargs.get('pk'), form_status = '3')
        data['type'] = self.kwargs.get('type')

        return data

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def write_pdf_view(request):
    doc = SimpleDocTemplate("/tmp/somefilename.pdf")
    styles = getSampleStyleSheet()
    Story = [Spacer(1,2*inch)]
    style = styles["Normal"]
    for i in range(100):
       bogustext = ("This is Paragraph number %s.  " % i) * 20
       p = Paragraph(bogustext, style)
       Story.append(p)
       Story.append(Spacer(1,0.2*inch))
    doc.build(Story)

    fs = FileSystemStorage("/tmp")
    with fs.open("somefilename.pdf") as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'
        return response

    return response