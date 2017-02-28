from django.db.models import Q
from django.forms.extras.widgets import SelectDateWidget
from django import forms
from django.utils.translation import ugettext_lazy as _
from onadata.apps.fieldsight.models import Site
from onadata.apps.logger.models import XForm
from .models import FieldSightXF, Stage, Schedule, FormGroup, FORM_STATUS


class AssignSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.project_id = kwargs.pop('project', None)
        try:
            self.form_site = kwargs.get('instance').site.id
        except:
            self.form_site = 0
        super(AssignSettingsForm, self).__init__(*args, **kwargs)
        if self.project_id is not None:
            sites = Site.objects.filter(project__id=self.project_id).exclude(pk=self.form_site)
        else:
            sites = Site.objects.all()
        self.fields['site'].choices = [(obj.id, obj.name) for obj in sites]
        self.fields['site'].empty_label = None

    class Meta:
        fields = ['site']
        model = FieldSightXF


class FormTypeForm(forms.ModelForm):

    CHOICES = [(3, 'Normal Form'),
             (2, 'Schedule Form'),
            (1, 'Stage Form')]

    form_type = forms.ChoiceField(error_messages={'required': 'Please Choose Form Type !'},
                                  choices=CHOICES, widget=forms.RadioSelect())

    class Meta:
        fields = ['form_type']
        model = FieldSightXF


class FormStageDetailsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FormStageDetailsForm, self).__init__(*args, **kwargs)
        obj_list = Stage.objects.filter(stage__isnull=False, fieldsightxf__isnull=True)
        self.fields['stage'].choices = [(obj.id, obj.name) for obj in obj_list if not obj.form_exists()]
        self.fields['stage'].empty_label = None

    class Meta:
        fields = ['stage']
        model = FieldSightXF


class FormScheduleDetailsForm(forms.ModelForm):
    class Meta:
        fields = ['schedule']
        model = FieldSightXF


class FSFormForm(forms.ModelForm):

    class Meta:
        exclude = ['site']
        model = FieldSightXF


class GeneralFSForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(GeneralFSForm, self).__init__(*args, **kwargs)
        if hasattr(self.request, "project") and self.request.project is not None:
            xform = XForm.objects.filter(
                Q(user=self.request.user) | Q(fieldsightformlibrary__is_global=True) |
                Q(fieldsightformlibrary__project=self.request.project) |
                Q(fieldsightformlibrary__organization=self.request.organization))

        elif hasattr(self.request, "organization") and self.request.organization is not None:
            xform = XForm.objects.filter(
                Q(user=self.request.user) |
                Q(fieldsightformlibrary__is_global=True) |
                Q(fieldsightformlibrary__organization=self.request.organization))
        else:
            xform = XForm.objects.filter(
                Q(user=self.request.user) | Q(fieldsightformlibrary__is_global=True))
        self.fields['xf'].choices = [(obj.id, obj.title) for obj in xform]
        self.fields['xf'].empty_label = None
        self.fields['xf'].label = "Form"

    class Meta:
        fields = ['xf']
        model = FieldSightXF

    def clean(self):
        if FieldSightXF.objects.filter(xf=self.data['xf'], is_staged=False, is_scheduled=False,
                        site=self.instance.site, project=self.instance.project).exists():
            if not FieldSightXF.objects.get(xf=self.data['xf'], is_staged=False, is_scheduled=False,
                        site=self.instance.site, project=self.instance.project).pk == self.instance.pk:
                raise forms.ValidationError({
                    'xf': forms.ValidationError(_('General Form Already Exists.'), code='invalid'),
                })


class StageForm(forms.ModelForm):

    class Meta:
        exclude = ['group', 'stage', 'site', 'shared_level', 'project', 'ready']
        model = Stage


class MainStageEditForm(forms.ModelForm):

    class Meta:
        exclude = ['group', 'stage', 'site', 'shared_level', 'project', 'ready', 'order']
        model = Stage


class SubStageEditForm(forms.ModelForm):
    form = forms.ChoiceField(widget = forms.Select(), required=False,)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SubStageEditForm, self).__init__(*args, **kwargs)
        if hasattr(self.request, "project") and self.request.project is not None:
            xform = XForm.objects.filter(
                Q(user=self.request.user) | Q(fieldsightformlibrary__is_global=True) |
                Q(fieldsightformlibrary__project=self.request.project) |
                Q(fieldsightformlibrary__organization=self.request.organization))

        elif hasattr(self.request, "organization") and self.request.organization is not None:
            xform = XForm.objects.filter(
                Q(user=self.request.user) |
                Q(fieldsightformlibrary__is_global=True) |
                Q(fieldsightformlibrary__organization=self.request.organization))
        else:
            xform = XForm.objects.filter(
                Q(user=self.request.user) | Q(fieldsightformlibrary__is_global=True))
        self.fields['form'].choices = [(obj.id, obj.title) for obj in xform]
        self.fields['form'].empty_label = None


    class Meta:
        exclude = ['group', 'stage', 'site', 'shared_level', 'project', 'ready', 'order']
        model = Stage


class AddSubSTageForm(forms.ModelForm):
    form = forms.ChoiceField(widget = forms.Select(), required=False,)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AddSubSTageForm, self).__init__(*args, **kwargs)
        if hasattr(self.request, "project") and self.request.project is not None:
            xform = XForm.objects.filter(
                Q(user=self.request.user) | Q(fieldsightformlibrary__is_global=True) |
                Q(fieldsightformlibrary__project=self.request.project) |
                Q(fieldsightformlibrary__organization=self.request.organization))

        elif hasattr(self.request, "organization") and self.request.organization is not None:
            xform = XForm.objects.filter(
                Q(user=self.request.user) |
                Q(fieldsightformlibrary__is_global=True) |
                Q(fieldsightformlibrary__organization=self.request.organization))
        else:
            xform = XForm.objects.filter(
                Q(user=self.request.user) | Q(fieldsightformlibrary__is_global=True))
        self.fields['form'].choices = [(obj.id, obj.title) for obj in xform]
        self.fields['form'].empty_label = None


    class Meta:
        exclude = ['stage', 'group', 'shared_level', 'site', 'project', 'ready']
        model = Stage


class AssignFormToStageForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AssignFormToStageForm, self).__init__(*args, **kwargs)
        xf_list = XForm.objects.all()
        self.fields['xf'].choices = [(f.id,f.title) for f in xf_list]
        self.fields['xf'].empty_label = None

    class Meta:
        fields = ['xf','site','is_staged','is_scheduled','stage']
        model = FieldSightXF
        labels = {
            "xf": _("Select Form"),
        }
        widgets = {'site': forms.HiddenInput(),
                   'is_staged': forms.HiddenInput(),
                   'is_scheduled': forms.HiddenInput(),
                   'stage': forms.HiddenInput()}


class AssignFormToScheduleForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AssignFormToScheduleForm, self).__init__(*args, **kwargs)
        xf_list = XForm.objects.all()
        self.fields['xf'].choices = [(xf.id, xf.title) for xf in xf_list]
        self.fields['xf'].empty_label = None

    class Meta:
        fields = ['xf','site','is_staged','is_scheduled', 'schedule']
        model = FieldSightXF
        labels = {
            "xf": _("Select Form"),
        }
        widgets = {'site': forms.HiddenInput(),
                   'is_staged': forms.HiddenInput(),
                   'is_scheduled': forms.HiddenInput(),
                   'schedule': forms.HiddenInput()}

BIRTH_YEAR_CHOICES = ('1980', '1981', '1982')


class ScheduleForm(forms.ModelForm):
    form = forms.ChoiceField(widget = forms.Select(), required=False,)
    form_type = forms.ChoiceField("Select Form Type",widget = forms.Select(
        attrs={'id':'form_type','onchange':'Hide()'}), required=False,)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ScheduleForm, self).__init__(*args, **kwargs)
        if hasattr(self.request, "project") and self.request.project is not None:
            xform = XForm.objects.filter(
                Q(user=self.request.user) | Q(fieldsightformlibrary__is_global=True) |
                Q(fieldsightformlibrary__project=self.request.project) |
                Q(fieldsightformlibrary__organization=self.request.organization))

        elif hasattr(self.request, "organization") and self.request.organization is not None:
            xform = XForm.objects.filter(
                Q(user=self.request.user) |
                Q(fieldsightformlibrary__is_global=True) |
                Q(fieldsightformlibrary__organization=self.request.organization))
        else:
            xform = XForm.objects.filter(
                Q(user=self.request.user) | Q(fieldsightformlibrary__is_global=True))
        self.fields['form'].choices = [(obj.id, obj.title) for obj in xform]
        self.fields['form_type'].choices = [(0, "General"),(1, "Scheduled")]
        self.fields['form'].empty_label = None

    class Meta:
        fields = ['form', 'form_type', 'name','date_range_start','date_range_end','selected_days','shared_level']
        model = Schedule
        widgets = { 'selected_days': forms.CheckboxSelectMultiple,
                    'date_range_start': SelectDateWidget,
                    'date_range_end': SelectDateWidget,
                    }
SHARED_LEVEL = [('' ,'None'),(0, 'Global'), (1, 'Organization'), (2, 'Project'), ]


class GroupForm(forms.ModelForm):
    shared_level = forms.ChoiceField(widget = forms.Select(), choices=(SHARED_LEVEL))

    class Meta:
        fields = ['name', 'description','shared_level']
        model = FormGroup


class GroupEditForm(forms.ModelForm):

    class Meta:
        fields = ['name', 'description', 'id']
        model = FormGroup

    widgets = {'id': forms.HiddenInput(),}


    def clean(self):
        if FormGroup.objects.filter(name=self.cleaned_data['name']).exists():
            if not FormGroup.objects.get(name=self.cleaned_data['name']).pk == self.instance.pk:
                raise forms.ValidationError(_("Name Already Exists"))


class AlterAnswerStatus(forms.Form):
    status = forms.ChoiceField(widget = forms.Select(),
                     choices = (FORM_STATUS), required = True,)
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':4, 'cols':15}))


