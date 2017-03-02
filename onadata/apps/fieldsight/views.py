from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.views.generic import ListView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.forms.forms import NON_FIELD_ERRORS
import django_excel as excel


from registration.backends.default.views import RegistrationView

from onadata.apps.fsforms.Submission import Submission
from onadata.apps.fsforms.models import FieldSightXF
from onadata.apps.userrole.models import UserRole
from onadata.apps.users.models import UserProfile
from .mixins import (LoginRequiredMixin, SuperAdminMixin, OrganizationMixin, ProjectMixin,
                     CreateView, UpdateView, DeleteView, OrganizationView as OView, ProjectView as PView,
                     group_required, OrganizationViewFromProfile)
from .models import Organization, Project, Site, ExtraUserDetail, BluePrints
from .forms import OrganizationForm, ProjectForm, SiteForm, RegistrationForm, SetOrgAdminForm, \
    SetProjectManagerForm, SetSupervisorForm, SetCentralEngForm, AssignOrgAdmin, UploadFileForm, BluePrintForm


@login_required
def dashboard(request):
    current_role = request.role
    if current_role:
        if current_role.group.name == "Site Supervisor":
            return HttpResponseRedirect(reverse("fieldsight:site-dashboard", kwargs={'pk': current_role.site.pk}))
        if current_role.group.name in ["Project Manager", "Central Engineer"]:
            return HttpResponseRedirect(reverse("fieldsight:project-dashboard", kwargs={'pk': current_role.project.pk}))
        if current_role.group.name == "Organization Admin":
            return HttpResponseRedirect(reverse("fieldsight:organization-dashboard",
                                                kwargs={'pk': current_role.organization.pk}))

    total_users = User.objects.all().count()
    total_organizations = Organization.objects.all().count()
    total_projects = Project.objects.all().count()
    total_sites = Site.objects.all().count()
    data = serialize('custom_geojson', Site.objects.all(), geometry_field='location',
                        fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone','id',))
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

@login_required
def organization_dashboard(request, pk):
    obj = Organization.objects.get(pk=pk)
    if not UserRole.objects.filter(user=request.user).filter(Q(group__name="Organization Admin", organization=obj)
                                                                     | Q(group__name="Super Admin")).exists():
        return dashboard(request)
    peoples_involved = User.objects.filter(user_profile__organization=obj, is_active=True).\
        order_by('first_name')
    sites = Site.objects.filter(project__organization=obj)
    data = serialize('custom_geojson', sites, geometry_field='location',
                     fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone', 'id'))
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
            rejected +=1
        elif form.form_status == 2:
            flagged +=1
        else:
            approved +=1

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
    if not UserRole.objects.filter(user=request.user).filter(
                    Q(group__name="Central Engineer", project=obj) |
                    Q(group__name="Project Manager", project=obj) |
                    Q(group__name="Organization Admin", organization=obj.organization)|
                    Q(group__name="Super Admin")).exists():
        return dashboard(request)
    peoples_involved = User.objects.filter(user_profile__organization=obj.organization, is_active=True).\
        order_by('first_name')
    sites = Site.objects.filter(project=obj)
    data = serialize('custom_geojson', sites, geometry_field='location',
                     fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone','id',))

    total_sites = len(sites)
    fs_forms = FieldSightXF.objects.filter(site__project=obj.id)
    fs_forms = list(fs_forms)
    outstanding = flagged = approved = rejected = 0
    for form in fs_forms:
        if form.form_status == 0:
            outstanding += 1
        elif form.form_status == 1:
            rejected +=1
        elif form.form_status == 2:
            flagged +=1
        else:
            approved +=1

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
    if not UserRole.objects.filter(user=request.user).filter(
        Q(group__name="Site Supervisor", site=obj) |
        Q(group__name="Central Engineer", project=obj.project) |
        Q(group__name="Project Manager", project=obj.project) |
        Q(group__name="Organization Admin", organization=obj.project.organization)|
        Q(group__name="Super Admin")).exists():
            return dashboard(request)

    peoples_involved = User.objects.filter(user_profile__organization=obj.project.organization, is_active=True).\
        order_by('first_name')
    data = serialize('custom_geojson', [obj], geometry_field='location',
                     fields=('name', 'public_desc', 'additional_desc', 'address', 'location', 'phone', 'id'))

    all, outstanding, flagged, approved, rejected = Submission.get_site_submission(pk)
    dashboard_data = {
        'obj': obj,
        'peoples_involved': peoples_involved,
        'outstanding': outstanding,
        'flagged': flagged,
        'approved': approved,
        'rejected': rejected,
        'all': all,
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


@group_required("Project")
def upload_sites(request, pk):
    form = UploadFileForm()
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            project = Project(pk=pk)
            try:
                sites = request.FILES['file'].get_records()
                with transaction.atomic():
                    for site in sites:
                        site = dict((k,v) for k,v in site.iteritems() if v is not '')
                        lat = site.get("longitude",85.3240)
                        long = site.get("latitude",27.7172)
                        location = Point(lat, long,srid=4326)
                        _site, created = Site.objects.get_or_create(identifier=str(site.get("id")), name=site.get("name"),
                                                                    project=project, type_id=1)
                        _site.description = site.get("description"),
                        _site.phone = site.get("phone")
                        _site.address = site.get("address")
                        _site.public_desc = site.get("public_desc"),
                        _site.additional_desc = site.get("additional_desc")
                        _site.location=location
                        _site.save()
                messages.info(request, 'Site Upload Succesfull')
                return HttpResponseRedirect(reverse('fieldsight:site-list'))
            except Exception as e:
                form.full_clean()
                form._errors[NON_FIELD_ERRORS] = form.error_class(['Sites Upload Failed, UnSupported Data'])
                messages.warning(request, 'Site Upload Failed, UnSupported Data ')
    return render(request, 'fieldsight/upload_sites.html',{'form':form, 'project':pk})

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

@login_required
def filter_users(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        role = request.POST.get('role')
        groups = Group.objects.all()
        object_list = User.objects.filter(is_active=True, pk__gt=0)
        if name:
            object_list = object_list.filter(
                Q(first_name__contains=name)|Q(last_name__contains=name) |Q(username__contains=name))
        if role and role!='0':
            object_list = object_list.filter(user_roles__group__id=role)
        if hasattr(request,"organization") and request.organization:
            object_list = object_list.filter(user_roles__organization=request.organization)
        return render(request, 'fieldsight/user_list.html',{'object_list':object_list,'groups':groups})
    return HttpResponseRedirect(reverse('fieldsight:user-list'))


class CreateUserView(LoginRequiredMixin, ProjectMixin, UserDetailView, RegistrationView):
    def register(self, request, form, *args, **kwargs):
        with transaction.atomic():
            new_user = super(CreateUserView, self).register(
                request, form, *args, **kwargs)
            is_active = form.cleaned_data['is_active']
            new_user.first_name = request.POST.get('name', '')
            new_user.is_active = is_active
            new_user.is_superuser = True
            new_user.save()
            created = False
            if hasattr(request, "organization"):
                if request.organization:
                    user_profile, created = UserProfile.objects.get_or_create(user=new_user, organization=request.organization)

            if not created:
                organization = int(form.cleaned_data['organization'])
                org = Organization.objects.get(pk=organization)
                user_profile, created = UserProfile.objects.get_or_create(user=new_user, organization=org)
        if created:
            return new_user
        return False


@login_required
def blue_prints(request, id):

    ImageFormSet = modelformset_factory(BluePrints, form=BluePrintForm, extra=5)

    if request.method == 'POST':

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
    else:
        formset = ImageFormSet(queryset=BluePrints.objects.none())
    return render(request, 'fieldsight/blueprints_form.html', {'formset': formset,'id': id},)
