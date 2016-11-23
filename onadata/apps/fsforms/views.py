from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.http import HttpResponse, HttpResponseForbidden, Http404, QueryDict

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from onadata.apps.fsforms.reports_util import get_instances_for_field_sight_form, build_export_context
from onadata.libs.utils.log import audit_log, Actions
from onadata.libs.utils.logger_tools import response_with_mimetype_and_name
from onadata.apps.fieldsight.mixins import group_required, LoginRequiredMixin, ProjectRequiredMixin, ProjectMixin, \
    CreateView, UpdateView, DeleteView, KoboFormsMixin, SiteMixin
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


class AssignedFormListView(ListView):
    def get_template_names(self):
        return ['fsforms/assigned_form_list.html']
    def get_queryset(self):
        # get site from role, get only forms from that site.
        return FieldSightXF.objects.filter(site__id= self.request.site.id)


class FormsListView(FormView, LoginRequiredMixin, ProjectMixin, MyProjectListView):
    pass


class AssignedFormsListView(FormView, LoginRequiredMixin, SiteMixin, AssignedFormListView):
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


class GroupCreateView(FormGroupView, LoginRequiredMixin, KoboFormsMixin, CreateViewWithUser):
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
            return HttpResponseRedirect(reverse("forms:schedule-list"))
    else:
        form = FormScheduleDetailsForm(instance=field_sight_form)
    return render(request, "fsforms/form_details_schedule.html", {'form': form})


# form related

def download_xform(request, pk):
    # if request.user.is_anonymous():
        # raises a permission denied exception, forces authentication
        # response= JsonResponse({'code': 401, 'message': 'Unauthorized User'})
        # return response
    fsxform = get_object_or_404(FieldSightXF,
                              pk__exact=pk)

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
        for media in cursor[index].get('_attachments',[]):
            if media:
                medias.append(media.get('download_url',''))
        cursor[index].update({'medias':medias})
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
    # import ipdb
    # ipdb.set_trace()

    return render(request, 'survey_report/fieldsight_export_html.html', context)


