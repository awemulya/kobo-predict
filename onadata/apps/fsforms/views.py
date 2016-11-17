from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from onadata.apps.fieldsight.mixins import group_required, LoginRequiredMixin, ProjectRequiredMixin, ProjectMixin, \
    CreateView, UpdateView, DeleteView, KoboFormsMixin
from .forms import AssignSettingsForm, FSFormForm, FormTypeForm, FormStageDetailsForm, FormScheduleDetailsForm, \
    StageForm, ScheduleForm, GroupForm, AddSubSTageForm, AssignFormToStageForm, AssignFormToScheduleForm
from .models import FieldSightXF, Stage, Schedule, FormGroup

TYPE_CHOICES = {3, 'Normal Form', 2, 'Schedule Form', 1, 'Stage Form'}


class UniqueXformMixin(object):
    def get_queryset(self):
        return FieldSightXF.objects.order_by('xf__id').distinct('xf__id')


class FSFormView(object):
    model = FieldSightXF
    success_url = reverse_lazy('forms:library-forms-list')
    form_class = FSFormForm


class MyLibraryListView(ListView):
    def get_queryset(self):
        return FieldSightXF.objects.filter(stage__isnull= True)


class LibraryFormsListView(FSFormView, LoginRequiredMixin, MyLibraryListView):
    pass


class FormView(object):
    model = FieldSightXF
    success_url = reverse_lazy('forms:forms-list')
    form_class = FSFormForm


class MyProjectListView(ListView):
    def get_template_names(self):
        return ['fsforms/my_project_form_list.html']
    def get_queryset(self):
        return FieldSightXF.objects.filter(site__project__id= self.request.project.id)


class FormsListView(FormView, LoginRequiredMixin, ProjectMixin, MyProjectListView):
    pass


class StageView(object):
    model = Stage
    success_url = reverse_lazy('forms:stage-list')
    form_class = StageForm


class MainSTagesOnly(ListView):
    def get_queryset(self):
        return Stage.objects.filter(stage= None)


class StageListView(StageView, LoginRequiredMixin, MainSTagesOnly):
    pass


class StageCreateView(StageView, LoginRequiredMixin, KoboFormsMixin, CreateView):
    pass


class StageUpdateView(StageView, LoginRequiredMixin, KoboFormsMixin, UpdateView):
    pass


class StageDeleteView(StageView,LoginRequiredMixin, KoboFormsMixin, DeleteView):
    pass


@login_required
@group_required('KoboForms')
def add_sub_stage(request, pk=None):
    stage = get_object_or_404(
        Stage, pk=pk)
    if request.method == 'POST':
        form = AddSubSTageForm(data=request.POST)
        if form.is_valid():
            child_stage = form.save(commit=False)
            child_stage.stage = stage
            child_stage.group = stage.group
            child_stage.save()
            messages.info(request, 'Sub Stage {} Saved.'.format(child_stage.name))
            return HttpResponseRedirect(reverse("forms:stage-detail", kwargs={'pk': stage.id}))
    else:
        form = AddSubSTageForm()
    return render(request, "fsforms/add_sub_stage.html", {'form': form, 'obj':stage})


@login_required
@group_required('KoboForms')
def stage_details(request, pk=None):
    stage = get_object_or_404(
        Stage, pk=pk)
    object_list = Stage.objects.filter(stage__id=stage.id).order_by('order')
    return render(request, "fsforms/stage_detail.html", {'obj': stage,'object_list':object_list})


@login_required
@group_required('KoboForms')
def stage_add_form(request, pk=None):
    stage = get_object_or_404(
        Stage, pk=pk)
    if request.method == 'POST':
        form = AssignFormToStageForm(request.POST)
        if form.is_valid():
            fsform = form.save()
            fsform.is_staged = True
            fsform.is_scheduled = False
            fsform.stage = stage
            fsform.save()
            messages.add_message(request, messages.INFO, 'Form Assigned Successfully.')
            return HttpResponseRedirect(reverse("forms:stage-detail", kwargs={'pk': stage.stage.id}))
    else:
        form = AssignFormToStageForm()
    return render(request, "fsforms/stage_add_form.html", {'form': form, 'obj':stage})


class ScheduleView(object):
    model = Schedule
    success_url = reverse_lazy('forms:schedule-list')
    form_class = ScheduleForm


class ScheduleListView(ScheduleView, LoginRequiredMixin, ListView):
    pass


class ScheduleCreateView(ScheduleView, LoginRequiredMixin, KoboFormsMixin, CreateView):
    pass


class ScheduleUpdateView(ScheduleView, LoginRequiredMixin, KoboFormsMixin, UpdateView):
    pass


class ScheduleDeleteView(ScheduleView,LoginRequiredMixin, KoboFormsMixin, DeleteView):
    pass


@login_required
@group_required('KoboForms')
def schedule_add_form(request, pk=None):
    schedule = get_object_or_404(
        Schedule, pk=pk)
    if request.method == 'POST':
        form = AssignFormToScheduleForm(request.POST)
        if form.is_valid():
            fsform = form.save()
            fsform.is_scheduled = True
            fsform.is_staged = False
            fsform.schedule = schedule
            fsform.save()
            messages.add_message(request, messages.INFO, 'Form Assigned Successfully.')
            return HttpResponseRedirect(reverse("forms:schedule-list"))
    else:
        form = AssignFormToScheduleForm()
    return render(request, "fsforms/schedule_add_form.html", {'form': form, 'obj':schedule})


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


class GroupCreateView(FormGroupView, LoginRequiredMixin, CreateViewWithUser):
    pass


class GroupUpdateView(FormGroupView, LoginRequiredMixin, KoboFormsMixin, UpdateView):
    pass


class GroupDeleteView(ScheduleView,LoginRequiredMixin, KoboFormsMixin, DeleteView):
    pass



@login_required
@group_required('KoboForms')
def assign(request, pk=None):
    field_sight_form = get_object_or_404(
        FieldSightXF, pk=pk)
    if request.method == 'POST':
        form = AssignSettingsForm(request.POST, instance=field_sight_form)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Form Assigned Successfully.')
            return HttpResponseRedirect(reverse("forms:fill_form_type", kwargs={'pk': form.instance.id}))
    else:
        form = AssignSettingsForm(instance=field_sight_form, project=request.project.id)
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
            if form_type == 3 :
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
    return render(request, "fsforms/stage_or_schedule.html", {'form': form, 'obj':field_sight_form})


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
            return HttpResponseRedirect(reverse("forms:stage-detail", kwargs={'pk': form.instance.stage.stage.id}))
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
            return HttpResponseRedirect(reverse("forms:fill-details-schedule", kwargs={'pk': form.instance.id}))
    else:
        form = FormScheduleDetailsForm(instance=field_sight_form)
    return render(request, "fsforms/form_details_schedule.html", {'form': form})

