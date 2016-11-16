
from django import forms
from django.utils.translation import ugettext_lazy as _
from onadata.apps.fieldsight.models import Site
from .models import FieldSightXF, Stage, Schedule, FormGroup


class AssignSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.project_id = kwargs.pop('project', None)
        super(AssignSettingsForm, self).__init__(*args, **kwargs)
        if self.project_id:
            sites = Site.objects.filter(project__id=self.project_id)
        else:
            sites = Site.objects.all()
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


class StageForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(StageForm, self).__init__(*args, **kwargs)
        stage = Stage.objects.all()
        obj_list = Stage.objects.filter(stage__isnull=True)
        self.fields['stage'].choices = [(obj.id, obj.name) for obj in obj_list]
        self.fields['stage'].empty_label = "This Is A Main Stage"
        self.fields['group'].empty_label = None


    class Meta:
        exclude = []
        model = Stage


class AddSubSTageForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AddSubSTageForm, self).__init__(*args, **kwargs)
        self.fields['group'].empty_label = None

    class Meta:
        exclude = ['stage']
        model = Stage


class AssignFormToStageForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AssignFormToStageForm, self).__init__(*args, **kwargs)
        xf_list = FieldSightXF.objects.filter(site__isnull=True)
        self.fields['xf'].choices = [(f.xf.id,f.xf.title) for f in xf_list]
        self.fields['xf'].empty_label = None
        self.fields['site'].empty_label = None

    class Meta:
        fields = ['xf','site']
        model = FieldSightXF
        labels = {
            "xf": _("Select Form"),
        }


class ScheduleForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = Schedule

class GroupForm(forms.ModelForm):

    class Meta:
        exclude = ['creator']
        model = FormGroup
