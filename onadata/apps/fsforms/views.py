from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from onadata.apps.fieldsight.mixins import group_required, LoginRequiredMixin
from .forms import AssignSettingsForm, FSFormForm, FillFormDetailsSettingsForm
from .models import FieldSightXF


class UniqueXformMixin(object):
    def get_queryset(self):
        return FieldSightXF.objects.order_by('xf__id').distinct('xf__id')


class FSFormView(object):
    model = FieldSightXF
    success_url = reverse_lazy('forms:library-forms-list')
    form_class = FSFormForm


class LibraryFormsListView(FSFormView, LoginRequiredMixin, ListView, UniqueXformMixin):
    pass


class FSFormsListView(FSFormView, LoginRequiredMixin, ListView):
    pass

@login_required
@group_required('KoboForms')
def assign(request, pk=None):
    fsform = get_object_or_404(
        FieldSightXF, pk=pk)
    if request.method == 'POST':
        form = AssignSettingsForm(request.POST, instance=fsform)
        if form.is_valid(): # All validation rules pass
            # access_list = form.cleaned_data['site']
            # xform.site.clear()
            # xform.site.add(*list(access_list))
            # if not access_list:
            #     messages.add_message(request, messages.WARNING, 'This Form Is assigned to None.')
            # else:
            import ipdb
            ipdb.set_trace()
            form.save()
            messages.add_message(request, messages.INFO, 'Form Assigned Suscesfully.')
            return HttpResponseRedirect(reverse("forms:fill_details", kwargs={'pk': form.instance.id}))
    else:
        form = AssignSettingsForm(instance=fsform, project=request.project.id)
    return render(request, "fsforms/assign.html", {'form': form})

@login_required
@group_required('KoboForms')
def fill_details(request, pk=None):
    fsform = get_object_or_404(
        FieldSightXF, pk=pk)
    if request.method == 'POST':
        form = FillFormDetailsSettingsForm(request.POST, instance=fsform)
        if form.is_valid(): # All validation rules pass
            # access_list = form.cleaned_data['site']
            # xform.site.clear()
            # xform.site.add(*list(access_list))
            # if not access_list:
            #     messages.add_message(request, messages.WARNING, 'This Form Is assigned to None.')
            # else:
            form.save()
            messages.add_message(request, messages.INFO, 'Form Assigned Suscesfully.')
            return HttpResponseRedirect(reverse("forms:fill_details", kwargs={'pk': form.instance.id}))
    else:
        form = FillFormDetailsSettingsForm(instance=fsform)
    return render(request, "fsforms/stage_or_schedule.html", {'form': form})

