from django import forms


class HTML5ModelForm(forms.ModelForm):
    required_css_class = 'required'

    class EmailTypeInput(forms.widgets.TextInput):
        input_type = 'email'

    class NumberTypeInput(forms.widgets.TextInput):
        input_type = 'number'

    class TelephoneTypeInput(forms.widgets.TextInput):
        input_type = 'tel'

    class DateTypeInput(forms.widgets.DateInput):
        input_type = 'date'

    class DateTimeTypeInput(forms.widgets.DateTimeInput):
        input_type = 'datetime'

    class TimeTypeInput(forms.widgets.TimeInput):
        input_type = 'time'

    def __init__(self, *args, **kwargs):
        self.exclude = kwargs.pop('exclude', None)
        super(HTML5ModelForm, self).__init__(*args, **kwargs)
        if self.exclude:
            del self.fields[self.exclude]
        self.refine()

    def refine(self):
        for (name, field) in self.fields.items():
            file_fields = [forms.fields.ImageField, forms.fields.FileField]
            # add HTML5 required attribute for required fields, except for file fields which already have a value
            if field.required and not (field.__class__ in file_fields and getattr(self.instance, name)):
                field.widget.attrs['required'] = 'required'

    def hide_field(self, request):
        for query in request.GET:
            if query[-3:] == '_id':
                query = query[:-3]
            self.fields[query].widget = self.fields[query].hidden_widget()
            self.fields[query].label = ''
        return self


class HTML5BootstrapModelForm(HTML5ModelForm):
    def refine(self):
        super(HTML5BootstrapModelForm, self).refine()
        for (name, field) in self.fields.items():
            widget = field.widget
            exclude_form_control = ['CheckboxInput', 'RadioSelect']
            if widget.__class__.__name__ in exclude_form_control:
                continue
            if 'class' in widget.attrs:
                widget.attrs['class'] += ' form-control'
            else:
                widget.attrs['class'] = 'form-control'


class KOModelForm(forms.ModelForm):
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(KOModelForm, self).__init__(*args, **kwargs)
        self.refine_for_ko()

    def refine_for_ko(self):
        for (name, field) in self.fields.items():
            # add HTML5 required attribute for required fields
            if field.required:
                field.widget.attrs['required'] = 'required'
            field.widget.attrs['data-bind'] = 'value: ' + name
