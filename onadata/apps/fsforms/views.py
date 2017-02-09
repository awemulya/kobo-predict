from bson import json_util
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.generic import ListView
from django.http import HttpResponse, HttpResponseForbidden, Http404, HttpResponseBadRequest

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from onadata.apps.fieldsight.models import Site, Project
from onadata.apps.fsforms.reports_util import get_instances_for_field_sight_form, build_export_context, \
    get_xform_and_perms, query_mongo, get_instance, update_status
from onadata.apps.fsforms.utils import send_message
from onadata.apps.logger.models import XForm
from onadata.libs.utils.user_auth import add_cors_headers
from onadata.libs.utils.user_auth import helper_auth_helper
from onadata.libs.utils.log import audit_log, Actions
from onadata.libs.utils.logger_tools import response_with_mimetype_and_name
from onadata.apps.fieldsight.mixins import group_required, LoginRequiredMixin, ProjectMixin, \
    CreateView, UpdateView, DeleteView, KoboFormsMixin, SiteMixin, OrganizationOrProjectRequiredMixin, ProjectView
from .forms import AssignSettingsForm, FSFormForm, FormTypeForm, FormStageDetailsForm, FormScheduleDetailsForm, \
    StageForm, ScheduleForm, GroupForm, AddSubSTageForm, AssignFormToStageForm, AssignFormToScheduleForm, \
    AlterAnswerStatus, MainStageEditForm, SubStageEditForm
from .models import FieldSightXF, Stage, Schedule, FormGroup, FieldSightFormLibrary

TYPE_CHOICES = {3, 'Normal Form', 2, 'Schedule Form', 1, 'Stage Form'}


class UniqueXformMixin(object):
    def get_queryset(self):
        return FieldSightXF.objects.order_by('xf__id').distinct('xf__id')


class FSFormView(object):
    model = XForm
    success_url = reverse_lazy('forms:library-forms-list')
    form_class = FSFormForm


class OwnListView(ListView):
    def get_template_names(self):
        return ['fsforms/my_form_list.html']
    def get_queryset(self):
        return XForm.objects.filter(user=self.request.user).order_by('title')


class LibraryFormView(object):
    model = FieldSightFormLibrary
    success_url = reverse_lazy('forms:library-forms-list')


class MyLibraryListView(ListView):
    def get_template_names(self):
        return ['fsforms/library_form_list.html']


class LibraryFormsListView(LibraryFormView, ProjectView, MyLibraryListView, ProjectMixin):
    pass


class MyOwnFormsListView(FSFormView, OwnListView):
    pass

class FormView(object):
    model = FieldSightXF
    success_url = reverse_lazy('forms:forms-list')
    form_class = FSFormForm


@login_required
@require_POST
def share_level(request, id, counter):
    xf = XForm.objects.get(id_string=id)
    # sl = dict(request.POST).get('sl')[int(counter)-1]
    sl = request.POST.get('sl')
    if not FieldSightFormLibrary.objects.filter(xf__id_string=id).exists():
        form = FieldSightFormLibrary()
        form.xf= xf
    else:
        form = FieldSightFormLibrary.objects.get(xf__id_string=id)
    if not sl:
        if form.pk:
            form.delete()
            messages.add_message(request, messages.WARNING, '{0} Form Shared Removed'.format(xf.title))
    else:
        if sl == '0':
            form.is_global = True
            form.organization = None
            form.project = None
            form.save()
            messages.add_message(request, messages.INFO, '{0} Shared Globally '.format(xf.title))
        elif sl == '1':
            form.is_global = False
            if hasattr(request,"project") and request.project:
                form.organization = request.project.organization
                form.project = None
                form.save()
                messages.add_message(request, messages.INFO, '{0} Shared To Organization Level'.format(xf.title))
            elif hasattr(request,"organization") and request.organization:
                form.organization = request.organization
                form.project = None
                form.save()
                messages.add_message(request, messages.INFO, '{0} Shared To Organization Level'.format(xf.title))
            else:
                messages.add_message(request, messages.WARNING, '{0} Not Shared. You Cannot Share to Project Level'.
                                     format(xf.title))
        else:
            if hasattr(request,"project") and request.project:
                form.is_global  = False
                form.organization = request.project.organization
                form.project = request.project
                form.save()
                messages.add_message(request, messages.INFO, '{0} Shared to Project Level '.format(xf.title))
            else:
                messages.add_message(request, messages.WARNING, '{0} Form Not Shared. You Cannot Share to Project Level'
                                     .format(xf.title))

    return HttpResponseRedirect(reverse('forms:forms-list'))

class MyProjectListView(ListView):
    def get_template_names(self):
        return ['fsforms/my_project_form_list.html']

    def get_queryset(self):
        if self.request.site:
            return FieldSightXF.objects.filter(site__id=self.request.site.id)
        elif self.request.project:
            return FieldSightXF.objects.filter(site__project__id=self.request.project.id)
        elif self.request.organization:
            return FieldSightXF.objects.filter(site__project__organization__id=self.request.organization.id)
        else: return FieldSightXF.objects.filter(site__isnull=False)


class AssignedFormListView(ListView):
    def get_template_names(self):
        return ['fsforms/assigned_form_list.html']

    def get_queryset(self):
        return FieldSightXF.objects.filter(site__id=self.request.site.id)


class FormsListView(FormView, LoginRequiredMixin, SiteMixin, MyProjectListView):
    pass


class AssignedFormsListView(FormView, LoginRequiredMixin, SiteMixin, AssignedFormListView):
    pass


class StageView(object):
    model = Stage
    success_url = reverse_lazy('forms:stages-list')
    form_class = StageForm


class MainSTagesOnly(ListView):
    def get_queryset(self):
        return Stage.objects.filter(stage=None)


class StageListView(StageView, LoginRequiredMixin, MainSTagesOnly):
    pass


class StageCreateView(StageView, LoginRequiredMixin, KoboFormsMixin, CreateView):
    pass


class StageUpdateView(StageView, LoginRequiredMixin, KoboFormsMixin, UpdateView):
    pass


class StageDeleteView(StageView, LoginRequiredMixin, KoboFormsMixin, DeleteView):
    pass


@login_required
# @group_required('KoboForms')
def add_sub_stage(request, pk=None):
    stage = get_object_or_404(
        Stage, pk=pk)
    if request.method == 'POST':
        form = AddSubSTageForm(data=request.POST)
        if form.is_valid():
            child_stage = form.save(commit=False)
            child_stage.stage = stage
            child_stage.project = stage.project
            child_stage.site = stage.site
            child_stage.group = stage.group
            child_stage.save()
            form = int(form.cleaned_data.get('form',0))
            if form:
                if stage.site:
                    FieldSightXF.objects.create(xf_id=form, is_staged=True, stage=child_stage,site=stage.site)
                else:
                    FieldSightXF.objects.create(xf_id=form, is_staged=True, stage=child_stage,project=stage.project)
            messages.info(request, 'Sub Stage {} Saved.'.format(child_stage.name))
            return HttpResponseRedirect(reverse("forms:stages-detail", kwargs={'pk': stage.id}))
    order = Stage.objects.filter(stage=stage).count() + 1
    instance = Stage(name="Sub Stage"+str(order), order=order)
    form = AddSubSTageForm(instance=instance)
    return render(request, "fsforms/add_sub_stage.html", {'form': form, 'obj': stage})


@login_required
# @group_required('KoboForms')
def stage_add(request, site_id=None):
    site = get_object_or_404(
        Site, pk=site_id)
    if request.method == 'POST':
        form = StageForm(data=request.POST)
        if form.is_valid():
            stage = form.save()
            stage.site = site
            stage.save()
            messages.info(request, 'Stage {} Saved.'.format(stage.name))
            return HttpResponseRedirect(reverse("forms:setup-site-stages", kwargs={'site_id': site.id}))
    order = Stage.objects.filter(site=site,stage__isnull=True).count() + 1
    instance = Stage(name="Stage"+str(order), order=order)
    form = StageForm(instance=instance)
    return render(request, "fsforms/stage_form.html", {'form': form, 'obj': site})


@login_required
# @group_required('KoboForms')
def responses(request, site_id=None):
    schedules = FieldSightXF.objects.filter(site_id=site_id, xf__isnull=False, is_scheduled=True)
    stages = Stage.objects.filter(stage__isnull=True, site_id=site_id).order_by('order')
    return render(request, "fsforms/responses_list.html", {'schedules': schedules, 'stages':stages, 'site': site_id})


@login_required
# @group_required('KoboForms')
def project_stage_add(request, id=None):
    project = get_object_or_404(
        Project, pk=id)
    if request.method == 'POST':
        form = StageForm(data=request.POST)
        if form.is_valid():
            stage = form.save()
            stage.project = project
            stage.save()
            messages.info(request, 'Stage {} Saved.'.format(stage.name))
            return HttpResponseRedirect(reverse("forms:setup-project-stages", kwargs={'id': project.id}))
    order = Stage.objects.filter(project=project,stage__isnull=True).count() + 1
    instance = Stage(name="Stage"+str(order), order=order)
    form = StageForm(instance=instance)
    return render(request, "fsforms/project/stage_form.html", {'form': form, 'obj': project})


@login_required
@group_required('KoboForms')
def stage_details(request, pk=None):
    stage = get_object_or_404(
        Stage, pk=pk)
    object_list = Stage.objects.filter(stage__id=stage.id).order_by('order')
    order = Stage.objects.filter(stage=stage).count() + 1
    instance = Stage(name="Sub Stage"+str(order), order=order)
    form = AddSubSTageForm(instance=instance)
    return render(request, "fsforms/stage_detail.html", {'obj': stage, 'object_list':object_list, 'form':form})


@login_required
def stage_add_form(request, pk=None):
    stage = get_object_or_404(
        Stage, pk=pk)
    if stage.stage.site:
        instance = FieldSightXF(site=stage.stage.site, is_staged=True, is_scheduled=False, stage=stage)
        if request.method == 'POST':
            form = AssignFormToStageForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'Form Assigned Successfully.')
                return HttpResponseRedirect(reverse("forms:stages-detail", kwargs={'pk': stage.stage.id}))
        else:
            form = AssignFormToStageForm(instance=instance)
        return render(request, "fsforms/stage_add_form.html", {'form': form, 'obj': stage})
    else:
        if request.method == 'POST':
            form = AssignFormToStageForm(request.POST)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'Form Assigned Successfully.')
                return HttpResponseRedirect(reverse("forms:stages-detail", kwargs={'pk': stage.stage.id}))
        else:
            form = AssignFormToStageForm()
        return render(request, "fsforms/stage_add_form.html", {'form': form, 'obj': stage})

@login_required
def edit_main_stage(request, stage, id, is_project):
    stage = get_object_or_404(Stage, pk=stage)
    if request.method == 'POST':
        form = MainStageEditForm(instance=stage, data=request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, 'Stage Updated.')
            if is_project == '1':
                return HttpResponseRedirect(reverse("forms:setup-project-stages", kwargs={'id': id}))
            else:
                return HttpResponseRedirect(reverse("forms:setup-site-stages", kwargs={'site_id': id}))
    form = MainStageEditForm(instance=stage)
    return render(request, "fsforms/main_stage_edit.html", {'form': form, 'id': id, 'is_project':is_project,'scenario':"Update"})

@login_required
def edit_sub_stage(request, stage, id, is_project):
    stage = get_object_or_404(Stage, pk=stage)
    if request.method == 'POST':
        form = SubStageEditForm(instance=stage, data=request.POST)
        if form.is_valid():
            form.save()
            form = int(form.cleaned_data.get('form',0))
            if form:
                if is_project:
                    if FieldSightXF.objects.filter(project=stage.project, stage=stage, is_staged=True).exists():
                        fsxform = FieldSightXF.objects.get(project=stage.project, stage=stage, is_staged=True)
                        fsxform.xf_id = form
                        fsxform.save()
                    else:
                        FieldSightXF.objects.create(xf_id=form, is_staged=True,stage=stage,project=stage.project)
                else:
                    if FieldSightXF.objects.filter(site=stage.site, stage=stage, is_staged=True).exists():
                        fsxform = FieldSightXF.objects.get(site=stage.site, stage=stage, is_staged=True)
                        fsxform.xf_id = form
                        fsxform.save()
                    else:
                        FieldSightXF.objects.create(xf_id=form, is_staged=True,stage=stage,site=stage.site)
            messages.info(request, 'Stage {} Updated.'.format(stage.name))
            return HttpResponseRedirect(reverse("forms:stages-detail", kwargs={'pk': stage.stage.id}))
    form = SubStageEditForm(instance=stage)
    if FieldSightXF.objects.filter(stage=stage).exists():
        if FieldSightXF.objects.get(stage=stage).xf:
            form.fields['form'].initial= FieldSightXF.objects.get(stage=stage).xf.id
    return render(request, "fsforms/sub_stage_edit.html", {'form': form, 'id': id, 'is_project':is_project,'scenario':"Update"})

@login_required
def create_schedule(request, site_id):
    site = get_object_or_404(
        Site, pk=site_id)
    if request.method == 'POST':
        form = ScheduleForm(data=request.POST)
        if form.is_valid():
            schedule = form.save()
            schedule.site = site
            schedule.save()
            form = int(form.cleaned_data.get('form',0))
            if form:
                FieldSightXF.objects.create(xf_id=form, is_scheduled=True,schedule=schedule,site=site)
            messages.info(request, 'Schedule {} Saved.'.format(schedule.name))
            return HttpResponseRedirect(reverse("forms:site-survey", kwargs={'site_id': site.id}))
    form = ScheduleForm()
    return render(request, "fsforms/schedule_form.html", {'form': form, 'obj': site})

@login_required
def site_survey(request, site_id):
    objlist = Schedule.objects.filter(site__id=site_id)
    if not len(objlist):
        return HttpResponseRedirect(reverse("forms:schedule-add", kwargs={'site_id': site_id}))
    return render(request, "fsforms/schedule_list.html", {'object_list': objlist, 'site':Site.objects.get(pk=site_id)})


@login_required
def project_create_schedule(request, id):
    project = get_object_or_404(
        Project, pk=id)
    if request.method == 'POST':
        form = ScheduleForm(data=request.POST)
        if form.is_valid():
            schedule = form.save()
            schedule.project = project
            schedule.save()
            form = int(form.cleaned_data.get('form',0))
            if form:
                FieldSightXF.objects.create(xf_id=form, is_scheduled=True,schedule=schedule,project=project)
            messages.info(request, 'Schedule {} Saved.'.format(schedule.name))
            return HttpResponseRedirect(reverse("forms:project-survey", kwargs={'project_id': project.id}))
    form = ScheduleForm()
    return render(request, "fsforms/schedule_form.html", {'form': form, 'obj': project, 'is_project':True})

@login_required
def project_edit_schedule(request, id):
    schedule = get_object_or_404(
        Schedule, pk=id)
    if request.method == 'POST':
        form = ScheduleForm(data=request.POST)
        if form.is_valid():
            schedule.name = form.cleaned_data['name']
            schedule.date_range_start = form.cleaned_data['date_range_start']
            schedule.date_range_end = form.cleaned_data['date_range_end']
            schedule.selected_days.clear()
            schedule.selected_days = form.cleaned_data['selected_days']
            schedule.shared_level = form.cleaned_data['shared_level']
            schedule.save()
            form = int(form.cleaned_data.get('form',0))
            if form:
                if FieldSightXF.objects.filter(project=schedule.project, schedule=schedule, is_scheduled=True).exists():
                    fsxform = FieldSightXF.objects.get(project=schedule.project, schedule=schedule, is_scheduled=True)
                    fsxform.xf_id = form
                    fsxform.save()
                else:
                    FieldSightXF.objects.create(xf_id=form, is_scheduled=True,schedule=schedule,project=schedule.project)
            messages.info(request, 'Schedule {} Saved.'.format(schedule.name))
            return HttpResponseRedirect(reverse("forms:project-survey", kwargs={'project_id': schedule.project.id}))
    form = ScheduleForm(instance=schedule)
    if FieldSightXF.objects.filter(schedule=schedule).exists():
        if FieldSightXF.objects.get(schedule=schedule).xf:
            form.fields['form'].initial= FieldSightXF.objects.get(schedule=schedule).xf.id
    return render(request, "fsforms/schedule_form.html", {'form': form, 'obj': schedule.project, 'is_project':True})


@login_required
def edit_schedule(request, id):
    schedule = get_object_or_404(
        Schedule, pk=id)
    if request.method == 'POST':
        form = ScheduleForm(data=request.POST)
        if form.is_valid():
            schedule.name = form.cleaned_data['name']
            schedule.date_range_start = form.cleaned_data['date_range_start']
            schedule.date_range_end = form.cleaned_data['date_range_end']
            schedule.selected_days.clear()
            schedule.selected_days = form.cleaned_data['selected_days']
            schedule.shared_level = form.cleaned_data['shared_level']
            schedule.save()
            form = int(form.cleaned_data.get('form',0))
            if form:
                if FieldSightXF.objects.filter(site=schedule.site, schedule=schedule, is_scheduled=True).exists():
                    fsxform = FieldSightXF.objects.get(site=schedule.site, schedule=schedule, is_scheduled=True)
                    fsxform.xf_id = form
                    fsxform.save()
                else:
                    FieldSightXF.objects.create(xf_id=form, is_scheduled=True,schedule=schedule,site=schedule.site)
            messages.info(request, 'Schedule {} Saved.'.format(schedule.name))
            return HttpResponseRedirect(reverse("forms:site-survey", kwargs={'site_id': schedule.site.id}))
    form = ScheduleForm(instance=schedule)
    if FieldSightXF.objects.filter(schedule=schedule).exists():
        if FieldSightXF.objects.get(schedule=schedule).xf:
            form.fields['form'].initial= FieldSightXF.objects.get(schedule=schedule).xf.id
    return render(request, "fsforms/schedule_form.html", {'form': form, 'obj': schedule.site, 'is_project':False})


class ScheduleView(object):
    model = Schedule
    success_url = reverse_lazy('forms:schedules-list')
    form_class = ScheduleForm


class ScheduleListView(ScheduleView, LoginRequiredMixin, ListView):
    pass


class ScheduleCreateView(ScheduleView, LoginRequiredMixin, KoboFormsMixin, CreateView):
    pass
#
#
# class ScheduleUpdateView(ScheduleView, LoginRequiredMixin, KoboFormsMixin, UpdateView):
#     pass
#
#
# class ScheduleDeleteView(ScheduleView, LoginRequiredMixin, KoboFormsMixin, DeleteView):
#     pass


@login_required
@group_required('KoboForms')
def schedule_add_form(request, pk=None):
    schedule = get_object_or_404(
        Schedule, pk=pk)
    instance = FieldSightXF(site=schedule.site, is_staged=False, is_scheduled=True, schedule=schedule)
    if request.method == 'POST':
        form = AssignFormToScheduleForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Form Assigned Successfully.')
            return HttpResponseRedirect(reverse("forms:site-survey", kwargs={'site_id': schedule.site.id}))
    form = AssignFormToScheduleForm(instance=instance)
    return render(request, "fsforms/schedule_add_form.html", {'form': form, 'obj': schedule})


class FormGroupView(object):
    model = FormGroup
    success_url = reverse_lazy('forms:group-list')
    form_class = GroupForm


class GroupListView(FormGroupView, LoginRequiredMixin, ListView):
    pass


class CreateViewWithUser(CreateView):
    def dispatch(self, *args, **kwargs):
        return super(CreateViewWithUser, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.creator = self.request.user
        obj.save()
        return HttpResponseRedirect(self.success_url)


class GroupCreateView(FormGroupView, LoginRequiredMixin, KoboFormsMixin, CreateViewWithUser):
    pass


class GroupUpdateView(FormGroupView, LoginRequiredMixin, KoboFormsMixin, UpdateView):
    pass


class GroupDeleteView(ScheduleView,LoginRequiredMixin, KoboFormsMixin, DeleteView):
    pass



@login_required
# @group_required('KoboForms')
def site_forms(request, site_id=None):
    return render(request, "fsforms/site_forms_ng.html", {'site_id': site_id, 'angular_url':settings.ANGULAR_URL})


@login_required
# @group_required('KoboForms')
def site_stages(request, site_id=None):
    return render(request, "fsforms/site_stages_ng.html", {'site_id': site_id, 'angular_url':settings.ANGULAR_URL})


@login_required
@group_required('KoboForms')
def assign(request, pk=None):
    if request.method == 'POST':
        field_sight_form = get_object_or_404(
        FieldSightXF, pk=pk)
        form = AssignSettingsForm(request.POST, instance=field_sight_form)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Form Assigned Successfully.')
            return HttpResponseRedirect(reverse("forms:fill_form_type", kwargs={'pk': form.instance.id}))
    else:
        field_sight_form = FieldSightXF.objects.create(xf=XForm.objects.get(pk=int(pk)))
        project = request.project.id if request.project is not None else None
        form = AssignSettingsForm(instance=field_sight_form, project=project)
    return render(request, "fsforms/assign.html", {'form': form})


@login_required
@group_required('KoboForms')
def fill_form_type(request, pk=None):
    field_sight_form = get_object_or_404(
        FieldSightXF, pk=pk)
    if request.method == 'POST':
        form = FormTypeForm(request.POST)
        if form.is_valid():
            form_type = form.cleaned_data.get('form_type', '3')
            form_type = int(form_type)
            messages.info(request, 'Form Type Saved.')
            if form_type == 3:
                return HttpResponseRedirect(reverse("forms:library-forms-list"))
            elif form_type == 2:
                field_sight_form.is_scheduled = True
                field_sight_form.save()
                return HttpResponseRedirect(reverse("forms:fill_details_schedule", kwargs={'pk': field_sight_form.id}))
            else:
                field_sight_form.is_staged = True
                field_sight_form.save()
                return HttpResponseRedirect(reverse("forms:fill_details_stage", kwargs={'pk': field_sight_form.id}))
    else:
        form = FormTypeForm()
    return render(request, "fsforms/stage_or_schedule.html", {'form': form, 'obj': field_sight_form})


@login_required
@group_required('KoboForms')
def fill_details_stage(request, pk=None):
    field_sight_form = get_object_or_404(
        FieldSightXF, pk=pk)
    if request.method == 'POST':
        form = FormStageDetailsForm(request.POST, instance=field_sight_form)
        if form.is_valid():
            form.save()
            messages.info(request, 'Form Stage Saved.')
            return HttpResponseRedirect(reverse("forms:stages-detail", kwargs={'pk': form.instance.stage.stage.id}))
    else:
        form = FormStageDetailsForm(instance=field_sight_form)
    return render(request, "fsforms/form_details_stage.html", {'form': form})


@login_required
@group_required('KoboForms')
def fill_details_schedule(request, pk=None):
    field_sight_form = get_object_or_404(
        FieldSightXF, pk=pk)
    if request.method == 'POST':
        form = FormScheduleDetailsForm(request.POST, instance=field_sight_form)
        if form.is_valid():
            form.save()
            messages.info(request, 'Form Schedule Saved.')
            return HttpResponseRedirect(reverse("forms:schedules-list"))
    else:
        form = FormScheduleDetailsForm(instance=field_sight_form)
    return render(request, "fsforms/form_details_schedule.html", {'form': form})


def setup_site_stages(request, site_id):
    objlist = Stage.objects.filter(fieldsightxf__isnull=True, stage__isnull=True,site__id=site_id)
    order = Stage.objects.filter(site__id=site_id,stage__isnull=True).count() + 1
    instance = Stage(name="Stage"+str(order), order=order)
    form = StageForm(instance=instance)
    return render(request, "fsforms/main_stages.html",
                  {'objlist': objlist, 'site':Site(pk=site_id),'form': form})


def setup_project_stages(request, id):
    objlist = Stage.objects.filter(fieldsightxf__isnull=True, stage__isnull=True,project__id=id)
    order = Stage.objects.filter(project__id=id,stage__isnull=True).count() + 1
    instance = Stage(name="Stage"+str(order), order=order)
    form = StageForm(instance=instance)
    return render(request, "fsforms/project/project_main_stages.html",
                  {'objlist': objlist, 'obj':Project(pk=id), 'form': form})


def project_survey(request, project_id):
    objlist = Schedule.objects.filter(project__id=project_id)
    if not len(objlist):
        return HttpResponseRedirect(reverse("forms:project-schedule-add", kwargs={'id': project_id}))
    return render(request, "fsforms/project/schedule_list.html", {'object_list': objlist, 'project': Project(id=project_id)})


# form related

def download_xform(request, pk):
    # if request.user.is_anonymous():
        # raises a permission denied exception, forces authentication
        # response= JsonResponse({'code': 401, 'message': 'Unauthorized User'})
        # return response
    fsxform = get_object_or_404(FieldSightXF, pk__exact=pk)

    audit = {
        "xform": fsxform.pk
    }

    audit_log(
        Actions.FORM_XML_DOWNLOADED, request.user, fsxform.xf.user,
        _("Downloaded XML for form '%(pk)s'.") %
        {
            "pk": pk
        }, audit, request)
    response = response_with_mimetype_and_name('xml', pk,
                                               show_date=False)
    # from xml.etree.cElementTree import fromstring, tostring, ElementTree as ET, Element
    # tree = fromstring(fsxform.xf.xml)
    # head = tree.findall("./")[0]
    # model = head.findall("./")[1]
    # # model.append(Element('FormID', {'id': str(fsxform.id)}))
    # response.content = tostring(tree,encoding='utf8', method='xml')
    # # # import ipdb
    # # # ipdb.set_trace()
    response.content = fsxform.xf.xml

    return response


@group_required('KoboForms')
def html_export(request, fsxf_id):

    limit = int(request.REQUEST.get('limit', 100))
    fsxf_id = int(fsxf_id)
    fsxf = FieldSightXF.objects.get(pk=fsxf_id)
    xform = fsxf.xf
    id_string = xform.id_string
    cursor = get_instances_for_field_sight_form(fsxf_id)
    cursor = list(cursor)
    for index, doc in enumerate(cursor):
        medias = []
        for media in cursor[index].get('_attachments', []):
            if media:
                medias.append(media.get('download_url', ''))
        cursor[index].update({'medias': medias})
    paginator = Paginator(cursor, limit, request=request)

    try:
        page = paginator.page(request.REQUEST.get('page', 1))
    except (EmptyPage, PageNotAnInteger):
        try:
            page = paginator.page(1)
        except (EmptyPage, PageNotAnInteger):
            raise Http404('This report has no submissions')

    data = [("v1", page.object_list)]
    context = build_export_context(request, xform, id_string)

    context.update({
        'page': page,
        'table': [],
        'title': id,
    })

    export = context['export']
    sections = list(export.labels.items())
    section, labels = sections[0]
    id_index = labels.index('_id')

    # generator dublicating the "_id" to allow to make a link to each
    # submission
    def make_table(submissions):
        for chunk in export.parse_submissions(submissions):
            for section_name, rows in chunk.items():
                if section == section_name:
                    for row in rows:
                        yield row[id_index], row

    context['labels'] = labels
    context['data'] = make_table(data)
    context['fsxfid'] = fsxf_id
    context['obj'] = fsxf
    # return JsonResponse({'data': cursor})
    return render(request, 'fsforms/fieldsight_export_html.html', context)


def instance_detail(request, fsxf_id, instance_id):
    fsxf = FieldSightXF.objects.get(pk=fsxf_id)
    cursor = get_instance(instance_id)
    cursor = list(cursor)
    obj = cursor[0]
    _keys = ['_notes', 'meta/instanceID', 'end', '_uuid', '_bamboo_dataset_id', '_tags', 'start',
             '_geolocation', '_xform_id_string', '_userform_id', '_status', '__version__', 'formhub/uuid',
             '_id', 'fs_uuid', 'fs_site']
    data = {}
    medias = []
    status = 0
    for key in obj.keys():
        if key not in _keys:
            if key == "_attachments":
                for media in obj[key]:
                    if media:
                        medias.append(media.get('download_url', ''))
            elif key == "fs_status":
                status = obj[key]
            else:
                data.update({str(key): str(obj[key])})
    return render(request, 'fsforms/fieldsight_instance_export_html.html',
                  {'obj': fsxf, 'answer': instance_id, 'status': status, 'data': data, 'medias': medias})


def alter_answer_status(request, instance_id, status, fsid):
    if request.method == 'POST':
        form = AlterAnswerStatus(request.POST)
        if form.is_valid():
            status = int(form.cleaned_data['status'])
            update_status(instance_id, status)
            fsxf = FieldSightXF.objects.get(pk=fsid)
            fsxf.form_status = status
            fsxf.save()
            comment = form.cleaned_data['comment']
            if comment:
                # comment save
                pass
            send_message(fsxf, status, comment)
            return HttpResponseRedirect(reverse("forms:instance_detail",
                                                kwargs={'fsxf_id': fsid, 'instance_id':instance_id}))

    else:
        form = AlterAnswerStatus(initial={'status':status})

    return render(request, 'fsforms/alter_answer_status.html',
                  {'form': form, 'answer':instance_id, 'status':status, 'fsid':fsid})

# @group_required('KoboForms')
def instance(request, fsxf_id):

    fsxf_id = int(fsxf_id)
    xform, is_owner, can_edit, can_view = get_xform_and_perms(fsxf_id, request)
    # no access
    if not (xform.shared_data or can_view or
            request.session.get('public_link') == xform.uuid):
        return HttpResponseForbidden(_(u'Not shared.'))

    audit = {
        "xform": xform.id_string,
    }
    audit_log(
        Actions.FORM_DATA_VIEWED, request.user, xform.user,
        _("Requested instance view for '%(id_string)s'.") %
        {
            'id_string': xform.id_string,
        }, audit, request)
    return render(request, 'fieldsight_instance.html', {
        'username': request.user,
        'fsxf_id': fsxf_id,
        'xform': xform,
        'can_edit': can_edit
    })


@require_http_methods(["GET", "OPTIONS"])
def api(request, fsxf_id=None):
    """
    Returns all results as JSON.  If a parameter string is passed,
    it takes the 'query' parameter, converts this string to a dictionary, an
    that is then used as a MongoDB query string.

    NOTE: only a specific set of operators are allow, currently $or and $and.
    Please send a request if you'd like another operator to be enabled.

    NOTE: Your query must be valid JSON, double check it here,
    http://json.parser.online.fr/

    E.g. api?query='{"last_name": "Smith"}'
    """
    if request.method == "OPTIONS":
        response = HttpResponse()
        add_cors_headers(response)
        return response
    helper_auth_helper(request)
    fsxform = FieldSightXF.objects.get(pk=fsxf_id)
    xform = fsxform.xf
    # owner = request.user

    if not xform:
        return HttpResponseForbidden(_(u'Not shared.'))

    try:
        args = {
            'username': request.user.username,
            'id_string': xform.id_string,
            'query': request.GET.get('query'),
            'fields': request.GET.get('fields'),
            'sort': request.GET.get('sort')
        }
        if 'start' in request.GET:
            args["start"] = int(request.GET.get('start'))
        if 'limit' in request.GET:
            args["limit"] = int(request.GET.get('limit'))
        if 'count' in request.GET:
            args["count"] = True if int(request.GET.get('count')) > 0\
                else False
        if xform:
            args["fsxfid"] = fsxform.id
        cursor = query_mongo(**args)
    except ValueError as e:
        return HttpResponseBadRequest(e.__str__())
    records = list(record for record in cursor)
    response_text = json_util.dumps(records)

    if 'callback' in request.GET and request.GET.get('callback') != '':
        callback = request.GET.get('callback')
        response_text = ("%s(%s)" % (callback, response_text))

    response = HttpResponse(response_text, content_type='application/json')
    add_cors_headers(response)
    return response


@require_GET
def show(request, fsxf_id):
    return HttpResponse("Show form here, comming soon.")
    pass
    # if uuid:
    #     return redirect_to_public_link(request, uuid)
    # xform, is_owner, can_edit, can_view = get_xform_and_perms(
    #     username, id_string, request)
    # # no access
    # if not (xform.shared or can_view or request.session.get('public_link')):
    #     return HttpResponseRedirect(reverse(home))
    #
    # data = {}
    # data['cloned'] = len(
    #     XForm.objects.filter(user__username__iexact=request.user.username,
    #                          id_string__exact=id_string + XForm.CLONED_SUFFIX)
    # ) > 0
    # data['public_link'] = MetaData.public_link(xform)
    # data['is_owner'] = is_owner
    # data['can_edit'] = can_edit
    # data['can_view'] = can_view or request.session.get('public_link')
    # data['xform'] = xform
    # data['content_user'] = xform.user
    # data['base_url'] = "https://%s" % request.get_host()
    # data['source'] = MetaData.source(xform)
    # data['form_license'] = MetaData.form_license(xform).data_value
    # data['data_license'] = MetaData.data_license(xform).data_value
    # data['supporting_docs'] = MetaData.supporting_docs(xform)
    # data['media_upload'] = MetaData.media_upload(xform)
    # data['mapbox_layer'] = MetaData.mapbox_layer_upload(xform)
    # data['external_export'] = MetaData.external_export(xform)
    #
    #
    # if is_owner:
    #     set_xform_owner_data(data, xform, request, username, id_string)
    #
    # if xform.allows_sms:
    #     data['sms_support_doc'] = get_autodoc_for(xform)
    #
    # return render(request, "show.html", data)


# @group_required('KoboForms')
def download_jsonform(request, fsxf_id):
    fsxform = FieldSightXF.objects.get(pk=fsxf_id)
    xform = fsxform.xf

    if request.method == "OPTIONS":
        response = HttpResponse()
        add_cors_headers(response)
        return response
    helper_auth_helper(request)
    response = response_with_mimetype_and_name('json', xform.id_string,
                                               show_date=False)
    if 'callback' in request.GET and request.GET.get('callback') != '':
        callback = request.GET.get('callback')
        response.content = "%s(%s)" % (callback, xform.json)
    else:
        add_cors_headers(response)
        response.content = xform.json
    return response


@require_POST
@login_required
def delete_data(request, fsxf_id=None):
    pass
    # xform, owner = check_and_set_user_and_form(username, id_string, request)
    # response_text = u''
    # if not xform or not has_edit_permission(
    #     xform, owner, request, xform.shared
    # ):
    #     return HttpResponseForbidden(_(u'Not shared.'))
    #
    # data_id = request.POST.get('id')
    # if not data_id:
    #     return HttpResponseBadRequest(_(u"id must be specified"))
    #
    # Instance.set_deleted_at(data_id)
    # audit = {
    #     'xform': xform.id_string
    # }
    # audit_log(
    #     Actions.SUBMISSION_DELETED, request.user, owner,
    #     _("Deleted submission with id '%(record_id)s' "
    #         "on '%(id_string)s'.") %
    #     {
    #         'id_string': xform.id_string,
    #         'record_id': data_id
    #     }, audit, request)
    # response_text = json.dumps({"success": "Deleted data %s" % data_id})
    # if 'callback' in request.GET and request.GET.get('callback') != '':
    #     callback = request.GET.get('callback')
    #     response_text = ("%s(%s)" % (callback, response_text))
    #
    # return HttpResponse(response_text, content_type='application/json')



def data_view(request, fsxf_id):
    fsxform = FieldSightXF.objects.get(pk=fsxf_id)
    xform = fsxform.xf
    data = {
        'fsxf_id': fsxf_id,
        'owner': xform.user,
        'xform': xform,
        'obj': fsxform
    }
    audit = {
        "xform": xform.id_string,
    }
    audit_log(
        Actions.FORM_DATA_VIEWED, request.user, xform.user,
        _("Requested data view for '%(id_string)s'.") %
        {
            'id_string': xform.id_string,
        }, audit, request)

    return render(request, "fieldsight_data_view.html", data)