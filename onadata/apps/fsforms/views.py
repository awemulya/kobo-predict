from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from onadata.apps.fieldsight.mixins import group_required, LoginRequiredMixin, ProjectRequiredMixin, ProjectMixin
from .forms import AssignSettingsForm, FSFormForm, FormTypeForm
from .models import FieldSightXF

TYPE_CHOICES = {3, 'Normal Form', 2, 'Schedule Form', 1, 'Stage Form'}


class UniqueXformMixin(object):
    def get_queryset(self):
        return FieldSightXF.objects.order_by('xf__id').distinct('xf__id')


class FSFormView(object):
    model = FieldSightXF
    success_url = reverse_lazy('forms:library-forms-list')
    form_class = FSFormForm


class LibraryFormsListView(FSFormView, LoginRequiredMixin, ListView, UniqueXformMixin):
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
        form = FormTypeForm(request.POST, instance=field_sight_form)
        if form.is_valid():
            form_type = form.cleaned_data.get('form_type', '3')
            form_type = int(form_type)
            messages.info(request, 'Form Type Saved.')
            if form_type == 3 :
                return HttpResponseRedirect(reverse("forms:library-forms-list"))
            elif form_type == 2:
                field_sight_form.is_scheduled = True
                field_sight_form.save()
                return HttpResponseRedirect(reverse("forms:fill_details_schedule", kwargs={'pk': form.instance.id}))
            else:
                field_sight_form.is_staged = True
                field_sight_form.save()
                return HttpResponseRedirect(reverse("forms:fill_details_stage", kwargs={'pk': form.instance.id}))
    else:
        form = FormTypeForm(instance=field_sight_form)
    return render(request, "fsforms/stage_or_schedule.html", {'form': form})

