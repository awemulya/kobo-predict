from bson import json_util
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.db.models import Q
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
    get_xform_and_perms, query_mongo, get_instance, update_status, get_instances_for_project_field_sight_form
from onadata.apps.fsforms.utils import send_message
from onadata.apps.logger.models import XForm
from onadata.libs.utils.user_auth import add_cors_headers
from onadata.libs.utils.user_auth import helper_auth_helper
from onadata.libs.utils.log import audit_log, Actions
from onadata.libs.utils.logger_tools import response_with_mimetype_and_name
from onadata.apps.fieldsight.mixins import group_required, LoginRequiredMixin, ProjectMixin, \
    CreateView, UpdateView, DeleteView, KoboFormsMixin, SiteMixin
from .forms import AssignSettingsForm, FSFormForm, FormTypeForm, FormStageDetailsForm, FormScheduleDetailsForm, \
    StageForm, ScheduleForm, GroupForm, AddSubSTageForm, AssignFormToStageForm, AssignFormToScheduleForm, \
    AlterAnswerStatus, MainStageEditForm, SubStageEditForm, GeneralFSForm, GroupEditForm
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

    def get_queryset(self):
        if self.request.project:
            return super(MyLibraryListView, self).\
                get_queryset().filter(Q(is_global=True)
                                      | Q(project=self.request.project)
                                      |Q(organization=self.request.organization))
        elif self.request.organization:
            return super(MyLibraryListView, self).\
                get_queryset().filter(Q(is_global=True)
                                      |Q(organization=self.request.organization))
        else:
            return super(MyLibraryListView, self).get_queryset()

    def get_template_names(self):
        return ['fsforms/library_form_list.html']


class LibraryFormsListView(LibraryFormView, MyLibraryListView, ProjectMixin):
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
                messages.add_message(request, messages.WARNING, '{0} Not Shared. You Cannot Share to Organization Level'.
                                     format(xf.title))
        elif sl == '2':
            if hasattr(request,"project") and request.project:
                form.is_global  = False
                form.organization = None
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


class MainStagesOnly(ListView):
    def get_queryset(self):
        return Stage.objects.filter(stage=None)


class StageListView(StageView, LoginRequiredMixin, MainStagesOnly):
    pass


class StageCreateView(StageView, LoginRequiredMixin, KoboFormsMixin, CreateView):
    pass


class StageUpdateView(StageView, LoginRequiredMixin, KoboFormsMixin, UpdateView):
    pass


class StageDeleteView(StageView, LoginRequiredMixin, KoboFormsMixin, DeleteView):
    pass


@group_required("Project")
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
    form = AddSubSTageForm(instance=instance, request=request)
    return render(request, "fsforms/add_sub_stage.html", {'form': form, 'obj': stage})


@group_required("Project")
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


@group_required("Project")
def project_responses(request, project_id=None):
    schedules = FieldSightXF.objects.filter(project_id=project_id, xf__isnull=False, is_scheduled=True)
    stages = Stage.objects.filter(stage__isnull=True, project_id=project_id).order_by('order')
    generals = FieldSightXF.objects.filter(is_staged=False, is_scheduled=False,project_id=project_id)
    return render(request, "fsforms/project/project_responses_list.html",
                  {'schedules': schedules, 'stages':stages, 'generals':generals, 'project': project_id})


@group_required("Project")
def responses(request, site_id=None):
    schedules = FieldSightXF.objects.filter(site_id=site_id, xf__isnull=False, is_scheduled=True)
    stages = Stage.objects.filter(stage__isnull=True, site_id=site_id).order_by('order')
    generals = FieldSightXF.objects.filter(is_staged=False, is_scheduled=False,site_id=site_id)
    return render(request, "fsforms/responses_list.html",
                  {'schedules': schedules, 'stages':stages,'generals':generals, 'site': site_id})


@group_required("Project")
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


@group_required("Project")
def stage_details(request, pk=None):
    stage = get_object_or_404(
        Stage, pk=pk)
    object_list = Stage.objects.filter(stage__id=stage.id).order_by('order')
    order = Stage.objects.filter(stage=stage).count() + 1
    instance = Stage(name="Sub Stage"+str(order), order=order)
    form = AddSubSTageForm(instance=instance, request=request)
    return render(request, "fsforms/stage_detail.html", {'obj': stage, 'object_list':object_list, 'form':form})


@group_required("Project")
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


@group_required("Project")
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


@group_required("Project")
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
                        fs_xform = FieldSightXF.objects.get(project=stage.project, stage=stage, is_staged=True)
                        fs_xform.xf_id = form
                        fs_xform.save()
                    else:
                        FieldSightXF.objects.create(xf_id=form, is_staged=True,stage=stage,project=stage.project)
                else:
                    if FieldSightXF.objects.filter(site=stage.site, stage=stage, is_staged=True).exists():
                        fs_xform = FieldSightXF.objects.get(site=stage.site, stage=stage, is_staged=True)
                        fs_xform.xf_id = form
                        fs_xform.save()
                    else:
                        FieldSightXF.objects.create(xf_id=form, is_staged=True,stage=stage,site=stage.site)
            messages.info(request, 'Stage {} Updated.'.format(stage.name))
            return HttpResponseRedirect(reverse("forms:stages-detail", kwargs={'pk': stage.stage.id}))
    form = SubStageEditForm(instance=stage, request=request)
    if FieldSightXF.objects.filter(stage=stage).exists():
        if FieldSightXF.objects.get(stage=stage).xf:
            form.fields['form'].initial= FieldSightXF.objects.get(stage=stage).xf.id
    return render(request, "fsforms/sub_stage_edit.html", {'form': form, 'id': id, 'is_project':is_project,
                                                           'scenario':"Update"})


@group_required("Project")
def create_schedule(request, site_id):
    form = ScheduleForm(request=request)
    site = get_object_or_404(
        Site, pk=site_id)
    if request.method == 'POST':
        form = ScheduleForm(data=request.POST)
        if form.is_valid():
            form_type = int(form.cleaned_data.get('form_type',0))
            xf = int(form.cleaned_data.get('form', 0))
            if not form_type:
                if xf:
                    _, created = FieldSightXF.objects.get_or_create(xf_id=xf, is_scheduled=False,
                                                                    is_staged=False, site=site)
                    _.is_deployed= True
                    _.save()
                    messages.info(request, 'General Form  Saved.')
                return HttpResponseRedirect(reverse("forms:site-general", kwargs={'site_id': site.id}))
            schedule = form.save()
            schedule.site = site
            schedule.save()
            if xf:
                FieldSightXF.objects.create(xf_id=xf, is_scheduled=True,schedule=schedule,site=site, is_deployed=True)
            messages.info(request, 'Schedule {} Saved.'.format(schedule.name))
            return HttpResponseRedirect(reverse("forms:site-survey", kwargs={'site_id': site.id}))
    return render(request, "fsforms/schedule_form.html", {'form': form, 'obj': site, 'is_general':True})


@group_required("Project")
def site_survey(request, site_id):
    objlist = Schedule.objects.filter(site__id=site_id)
    if not len(objlist):
        return HttpResponseRedirect(reverse("forms:schedule-add", kwargs={'site_id': site_id}))
    return render(request, "fsforms/schedule_list.html", {'object_list': objlist, 'site':Site.objects.get(pk=site_id)})


@group_required("Project")
def site_general(request, site_id):
    objlist = FieldSightXF.objects.filter(site__id=site_id, is_staged=False, is_scheduled=False)
    if not len(objlist):
        return HttpResponseRedirect(reverse("forms:schedule-add", kwargs={'site_id': site_id}))
    return render(request, "fsforms/general_list.html", {'object_list': objlist, 'site':Site.objects.get(pk=site_id)})


@group_required("Project")
def project_general(request, project_id):
    objlist = FieldSightXF.objects.filter(project__id=project_id, is_staged=False, is_scheduled=False)
    if not len(objlist):
        return HttpResponseRedirect(reverse("forms:project-schedule-add", kwargs={'id': project_id}))
    return render(request, "fsforms/general_list.html", {'object_list': objlist, 'project':Project.objects.get(pk=project_id)})


@group_required("Project")
def project_create_schedule(request, id):
    project = get_object_or_404(
        Project, pk=id)
    if request.method == 'POST':
        form = ScheduleForm(data=request.POST)
        if form.is_valid():
            form_type = int(form.cleaned_data.get('form_type',0))
            xf = int(form.cleaned_data.get('form',0))
            if not form_type:
                if xf:
                    _, created = FieldSightXF.objects.get_or_create(
                        xf_id=xf, is_scheduled=False, is_staged=False, project=project)
                    _.is_deployed = True
                    _.save()
                    messages.info(request, 'General Form  Saved.')
                return HttpResponseRedirect(reverse("forms:project-general", kwargs={'project_id': project.id}))
            schedule = form.save()
            schedule.project = project
            schedule.save()
            if xf:
                FieldSightXF.objects.create(
                    xf_id=xf, is_scheduled=True,schedule=schedule,project=project, is_deployed=True)
            messages.info(request, 'Schedule {} Saved.'.format(schedule.name))
            return HttpResponseRedirect(reverse("forms:project-survey", kwargs={'project_id': project.id}))
    form = ScheduleForm(request=request)
    return render(request, "fsforms/schedule_form.html",
                  {'form': form, 'obj': project, 'is_project':True, 'is_general':True})


@group_required("Project")
def project_edit_schedule(request, id):
    schedule = get_object_or_404(
        Schedule, pk=id)
    if request.method == 'POST':
        form = ScheduleForm(data=request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            xf = int(form.cleaned_data.get('form', 0))
            if xf:
                if FieldSightXF.objects.filter(project=schedule.project, schedule=schedule, is_scheduled=True).exists():
                    fs_xform = FieldSightXF.objects.get(project=schedule.project, schedule=schedule, is_scheduled=True)
                    fs_xform.xf_id = xf
                    fs_xform.save()
                else:
                    FieldSightXF.objects.create(
                        xf_id=xf, is_scheduled=True,schedule=schedule,project=schedule.project, is_deployed=True)
            messages.info(request, 'Schedule {} Saved.'.format(schedule.name))
            return HttpResponseRedirect(reverse("forms:project-survey", kwargs={'project_id': schedule.project.id}))
    form = ScheduleForm(instance=schedule, request=request)
    if FieldSightXF.objects.filter(schedule=schedule).exists():
        if FieldSightXF.objects.get(schedule=schedule).xf:
            form.fields['form'].initial= FieldSightXF.objects.get(schedule=schedule).xf.id
    return render(request, "fsforms/schedule_form.html",
                  {'form': form, 'obj': schedule.project, 'is_project':True, 'is_general':False, 'is_edit':True})


@group_required("Project")
def edit_schedule(request, id):
    schedule = get_object_or_404(
        Schedule, pk=id)
    if request.method == 'POST':
        form = ScheduleForm(data=request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            xf = int(form.cleaned_data.get('form',0))
            if xf:
                if FieldSightXF.objects.filter(site=schedule.site, schedule=schedule, is_scheduled=True).exists():
                    fs_xform = FieldSightXF.objects.get(site=schedule.site, schedule=schedule, is_scheduled=True)
                    fs_xform.xf_id = xf
                    fs_xform.save()
                else:
                    FieldSightXF.objects.create(
                        xf_id=xf, is_scheduled=True,schedule=schedule,site=schedule.site, is_deployed=True)
            messages.info(request, 'Schedule {} Saved.'.format(schedule.name))
            return HttpResponseRedirect(reverse("forms:site-survey", kwargs={'site_id': schedule.site.id}))
    form = ScheduleForm(instance=schedule, request=request)
    if FieldSightXF.objects.filter(schedule=schedule).exists():
        if FieldSightXF.objects.get(schedule=schedule).xf:
            form.fields['form'].initial= FieldSightXF.objects.get(schedule=schedule).xf.id
    return render(request, "fsforms/schedule_form.html",
                  {'form': form, 'obj': schedule.site, 'is_project':False, 'is_general':False, 'is_edit':True})


@group_required("Project")
def set_deploy_stages(request, id):
    with transaction.atomic():
        FieldSightXF.objects.filter(is_staged=True, site__id=id).update(is_deployed=True)
        messages.info(request, 'Stages Form Deployed to Sites')
    return HttpResponseRedirect(reverse("forms:setup-site-stages", kwargs={'site_id': id}))


@group_required("Project")
def edit_share_stages(request, id):
    fgroup = get_object_or_404(
        FormGroup, pk=id)
    if request.method == 'POST':
        form = GroupEditForm(data=request.POST,instance=fgroup)
        if form.is_valid():
            group = form.save()
            sl = form.data['sl']
            if sl == '':
                group.is_global=False
                group.organization=None
                group.project=None
                group.save()

            if sl == '0':
                group.is_global= True
                group.organization=None
                group.project=None
                group.save()

            elif sl == '1':
                group.is_global = False
                if hasattr(request,"project") and request.project:
                    group.organization = request.project.organization
                    group.project = None
                    group.save()
                    messages.add_message(request, messages.INFO, '{0} Shared To Organization Level'.format(group.name))
                elif hasattr(request,"organization") and request.organization:
                    group.organization = request.organization
                    group.project = None
                    group.save()
                    messages.add_message(request, messages.INFO, '{0} Shared To Organization Level'.format(group.name))
                else:
                    messages.add_message(request, messages.WARNING, '{0} Not Shared. You Cannot Share to Organization Level'.
                                       format(group.name))
            elif sl == '2':
                if hasattr(request,"project") and request.project:
                    group.is_global  = False
                    group.organization = None
                    group.project = request.project
                    group.save()
                    messages.add_message(request, messages.INFO, '{0} Shared to Project Level '.format(group.name))
                else:
                    messages.add_message(request, messages.WARNING, '{0} Form Not Shared. You Cannot Share to Project Level'
                                         .format(group.name))

            return HttpResponseRedirect(reverse("forms:group-list"))
    sl = ''
    if fgroup.is_global:
        sl =  0
    elif fgroup.project:
        sl = 2
    elif fgroup.organization:
        sl = 1
    instance.shared_level = sl
    form = GroupEditForm(instance=fgroup)
    return render(request, "fsforms/edit_formgroup_form.html", {'form': form,'shared':sl})


@group_required("Project")
def share_stages(request, id, is_project):
    if request.method == 'POST':
        form = GroupForm(data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                group = form.save(commit=False)
                group.creator=request.user
                sl = form.cleaned_data['shared_level']
                if sl == '':
                    group.is_global=False
                    group.organization=None
                    group.project=None
                    group.save()

                if sl == '0':
                    group.is_global= True
                    group.organization=None
                    group.project=None
                    group.save()

                if sl == '1':
                    group.is_global= False
                    if is_project == '1':
                        group.organization = Project(pk=id).organization
                    else:
                        group.organization = Site(pk=id).project.organization
                    group.project=None
                    group.save()
                if sl == '2':
                    group.is_global= False
                    if is_project == '1':
                        group.project = Project(pk=id)
                    else:
                        group.project = Site(pk=id).project
                    group.organization=None
                    group.save()
                if is_project == '1':
                    Stage.objects.filter(stage__isnull=True,project_id=id).update(group=group)
                    messages.info(request, 'Project Stages Shared')
                    return HttpResponseRedirect(reverse("forms:setup-project-stages", kwargs={'id': id}))
                else:
                    Stage.objects.filter(stage__isnull=True,site_id=id).update(group=group)
                    messages.info(request, 'Site Stages Shared')
                    return HttpResponseRedirect(reverse("forms:setup-site-stages", kwargs={'site_id': id}))
    else:
        form = GroupForm()
    return render(request, "fsforms/formgroup_form.html", {'form': form,'is_project':is_project, 'id':id})


@group_required("Project")
def deploy_stages(request, id):
    project = Project(pk=id)
    sites = project.sites.all()
    main_stages = project.stages.filter(stage__isnull=True)
    with transaction.atomic():
        Stage.objects.filter(site__project=project).delete()
        FieldSightXF.objects.filter(is_staged=True, site__project=project).delete()
        for main_stage in main_stages:
            for site in sites:
                site_main_stage = Stage(name=main_stage.name, order=main_stage.order, site=site,
                                   description=main_stage.description)
                site_main_stage.save()
                project_sub_stages = Stage.objects.filter(stage__id=main_stage.pk)
                for project_sub_stage in project_sub_stages:
                    site_sub_stage = Stage(name=project_sub_stage.name, order=project_sub_stage.order, site=site,
                                   description=project_sub_stage.description, stage=site_main_stage)
                    site_sub_stage.save()
                    if FieldSightXF.objects.filter(stage=project_sub_stage).exists():
                        fsxf = FieldSightXF.objects.filter(stage=project_sub_stage)[0]
                        FieldSightXF.objects.get_or_create(is_staged=True, xf=fsxf.xf, site=site,
                                                           fsform=fsxf, stage=site_sub_stage, is_deployed=True)
    messages.info(request, 'Stages Form Deployed to Sites')
    return HttpResponseRedirect(reverse("forms:setup-project-stages", kwargs={'id': id}))


@group_required("Project")
def deploy_general(request, id):
    with transaction.atomic():
        fsxf = FieldSightXF.objects.get(pk=id)
        FieldSightXF.objects.filter(fsform=fsxf).delete()
        for site in fsxf.project.sites.filter(is_active=True):
            # cloning from parent
            child = FieldSightXF(is_staged=False, is_scheduled=False,xf=fsxf.xf, site=site, fsform_id=id, is_deployed=True)
            child.save()
    messages.info(request, 'General Form {} Deployed to Sites'.format(fsxf.xf.title))
    return HttpResponseRedirect(reverse("forms:project-general", kwargs={'project_id': fsxf.project.pk}))


@group_required("Project")
def deploy_survey(request, id):
    schedule = Schedule.objects.get(pk=id)
    selected_days = tuple(schedule.selected_days.all())
    fsxf = FieldSightXF.objects.get(schedule=schedule)
    with transaction.atomic():
        Schedule.objects.filter(fieldsightxf__fsform=fsxf).delete()
        FieldSightXF.objects.filter(fsform=fsxf).delete()
        for site in fsxf.project.sites.filter(is_active=True):
            _schedule = Schedule(name=schedule.name, site=site)
            _schedule.save()
            _schedule.selected_days.add(*selected_days)
            child = FieldSightXF(is_staged=False, is_scheduled=True,
                                 xf=fsxf.xf, site=site, fsform=fsxf, schedule=_schedule, is_deployed=True)
            child.save()
    messages.info(request, 'Schedule {} with  Form Named {} Form Deployed to Sites'.format(schedule.name,fsxf.xf.title))
    return HttpResponseRedirect(reverse("forms:project-survey", kwargs={'project_id': fsxf.project.id}))


@group_required("Project")
def edit_general(request, id):
    fs_xform = get_object_or_404(
        FieldSightXF, pk=id)
    if request.method == 'POST':
        form = GeneralFSForm(data=request.POST, instance=fs_xform)
        if form.is_valid():
            form.save()
            messages.info(request, 'General Form Updated')
            if fs_xform.site:
                return HttpResponseRedirect(reverse("forms:site-general", kwargs={'site_id': fs_xform.site.id}))
            return HttpResponseRedirect(reverse("forms:project-general", kwargs={'project_id': fs_xform.project.id}))
    form = GeneralFSForm(instance=fs_xform, request=request)
    is_project = True if fs_xform.project else False
    return render(request, "fsforms/general_form.html", {'form': form,'is_project':is_project})


@group_required("Project")
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
    form = AssignFormToScheduleForm(instance=instance, request=request)
    return render(request, "fsforms/schedule_add_form.html", {'form': form, 'obj': schedule})


class FormGroupView(object):
    model = FormGroup
    success_url = reverse_lazy('forms:group-list')
    form_class = GroupForm


class GroupListView(FormGroupView, LoginRequiredMixin, ListView):

    def get_queryset(self):
        if self.request.project:
            return super(GroupListView, self).\
                get_queryset().filter(Q(is_global=True)
                                      | Q(project=self.request.project)
                                      |Q(organization=self.request.organization))
        elif self.request.organization:
            return super(GroupListView, self).\
                get_queryset().filter(Q(is_global=True)
                                      |Q(organization=self.request.organization))
        else:
            return super(GroupListView, self).get_queryset()


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


class GroupDeleteView(FormGroupView, LoginRequiredMixin, KoboFormsMixin, DeleteView):
    pass


@group_required("Project")
def site_forms(request, site_id=None):
    return render(request, "fsforms/site_forms_ng.html", {'site_id': site_id, 'angular_url':settings.ANGULAR_URL})


@group_required("Project")
def site_stages(request, site_id=None):
    return render(request, "fsforms/site_stages_ng.html", {'site_id': site_id, 'angular_url':settings.ANGULAR_URL})


@group_required("Project")
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


@group_required("Project")
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


@group_required("Project")
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


@group_required("Project")
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


@group_required("Project")
def setup_site_stages(request, site_id):
    objlist = Stage.objects.filter(fieldsightxf__isnull=True, stage__isnull=True,site__id=site_id)
    order = Stage.objects.filter(site__id=site_id,stage__isnull=True).count() + 1
    instance = Stage(name="Stage"+str(order), order=order)
    form = StageForm(instance=instance)
    return render(request, "fsforms/main_stages.html",
                  {'objlist': objlist, 'site':Site(pk=site_id),'form': form})


@group_required("Project")
def library_stages(request, id):
    objlist = Stage.objects.filter(fieldsightxf__isnull=True, stage__isnull=True, group__id=id).order_by('order')
    return render(request, "fsforms/library_stage_detail.html", {'stages': objlist})


@group_required("Project")
def setup_project_stages(request, id):
    objlist = Stage.objects.filter(fieldsightxf__isnull=True, stage__isnull=True,project__id=id)
    order = Stage.objects.filter(project__id=id,stage__isnull=True).count() + 1
    instance = Stage(name="Stage"+str(order), order=order)
    form = StageForm(instance=instance)
    return render(request, "fsforms/project/project_main_stages.html",
                  {'objlist': objlist, 'obj':Project(pk=id), 'form': form})


@group_required("Project")
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
    fs_xform = get_object_or_404(FieldSightXF, pk__exact=pk)

    audit = {
        "xform": fs_xform.pk
    }

    audit_log(
        Actions.FORM_XML_DOWNLOADED, request.user, fs_xform.xf.user,
        _("Downloaded XML for form '%(pk)s'.") %
        {
            "pk": pk
        }, audit, request)
    response = response_with_mimetype_and_name('xml', pk,
                                               show_date=False)
    # from xml.etree.cElementTree import fromstring, tostring, ElementTree as ET, Element
    # tree = fromstring(fs_xform.xf.xml)
    # head = tree.findall("./")[0]
    # model = head.findall("./")[1]
    # # model.append(Element('FormID', {'id': str(fs_xform.id)}))
    # response.content = tostring(tree,encoding='utf8', method='xml')
    # # # import ipdb
    # # # ipdb.set_trace()
    response.content = fs_xform.xf.xml

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
    context['is_project'] = False
    # return JsonResponse({'data': cursor})
    return render(request, 'fsforms/fieldsight_export_html.html', context)


@group_required('KoboForms')
def project_html_export(request, fsxf_id):
    limit = int(request.REQUEST.get('limit', 100))
    fsxf_id = int(fsxf_id)
    fsxf = FieldSightXF.objects.get(pk=fsxf_id)
    xform = fsxf.xf
    id_string = xform.id_string
    cursor = get_instances_for_project_field_sight_form(fsxf_id)
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
    context['is_project'] = True
    # return JsonResponse({'data': cursor})
    return render(request, 'fsforms/fieldsight_export_html.html', context)



def instance_detail(request, fsxf_id, instance_id):
    fsxf = FieldSightXF.objects.get(pk=fsxf_id)
    cursor = get_instance(instance_id)
    cursor = list(cursor)
    obj = cursor[0]
    _keys = ['_notes', 'meta/instanceID', 'end', '_uuid', '_bamboo_dataset_id', '_tags', 'start',
             '_geolocation', '_xform_id_string', '_userform_id', '_status', '__version__', 'formhub/uuid',
             '_id', 'fs_uuid', 'fs_site', 'fs_project_uuid']
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
    fs_xform = FieldSightXF.objects.get(pk=fsxf_id)
    xform = fs_xform.xf
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
            args["fsxfid"] = fs_xform.id
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
    fs_xform = FieldSightXF.objects.get(pk=fsxf_id)
    xform = fs_xform.xf

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
    fs_xform = FieldSightXF.objects.get(pk=fsxf_id)
    xform = fs_xform.xf
    data = {
        'fsxf_id': fsxf_id,
        'owner': xform.user,
        'xform': xform,
        'obj': fs_xform
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