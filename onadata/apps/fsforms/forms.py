
from django import forms
from onadata.apps.fieldsight.models import Site
from .models import FieldSightXF

class AssignSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super(AssignSettingsForm, self).__init__(*args, **kwargs)
        sites = Site.objects.filter(project__id=self.project)

    class Meta:
        fields = ['site']
        model = FieldSightXF
        widgets = {
        'site': forms.CheckboxSelectMultiple()
        }