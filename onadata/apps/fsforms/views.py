from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from onadata.apps.fieldsight.mixins import group_required, LoginRequiredMixin
from .forms import AssignSettingsForm, FSFormForm
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
def assign(request, id_string=None):
    xform = get_object_or_404(
        FieldSightXF, xf__id_string=id_string)
    if request.method == 'POST':
        form = AssignSettingsForm(request.POST)
        if form.is_valid(): # All validation rules pass
            access_list = form.cleaned_data['site']
            xform.site.clear()
            xform.site.add(*list(access_list))
            if not access_list:
                messages.add_message(request, messages.WARNING, 'This Form Is assigned to None.')
            else:
                messages.add_message(request, messages.INFO, 'Form Assigned Suscesfully.')
            return HttpResponseRedirect(reverse("form_fill_details", kwargs={'pk': form.instance.id}))
    else:
        form = AssignSettingsForm(instance=xform, project=request.session['role'])
    return render(request, "assign.html", {'xform':xform,'form':form})

