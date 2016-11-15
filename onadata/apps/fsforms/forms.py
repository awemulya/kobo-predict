
from django import forms
from onadata.apps.fieldsight.models import Site
from .models import FieldSightXF


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
        exclude = ('site',)
        model = FieldSightXF
