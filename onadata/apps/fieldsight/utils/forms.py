from django import forms
from django.forms import widgets, Media
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.utils.html import format_html


class HorizontalCheckboxRenderer(forms.CheckboxSelectMultiple.renderer):
    def render(self):
        id_ = self.attrs.get('id', None)
        start_tag = format_html('<div id="{0}">', id_) if id_ else '<div>'
        output = [start_tag]
        for widget in self:
            output.append(format_html(u'<span>{0}</span>', force_text(widget)))
        output.append('</span>')
        return mark_safe('\n'.join(output))


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
            if isinstance(field, forms.fields.ImageField ):
                continue
            # add HTML5 required attribute for required fields
            if field.required:
                field.widget.attrs['required'] = 'required'
            field.widget.attrs['data-bind'] = 'value: ' + name


class HRBSFormField(widgets.TextInput):
    def __init__(self, attrs=None):
        # class_name = get_calendar() + '-date'
        # if attrs:
        #     attrs['class'] = class_name
        # else:
        #     attrs = {'class': class_name}
        super(HRBSFormField, self).__init__(attrs)

    def _media(self):
        css = {}
        js = ()
        return Media(css=css, js=js)

    def render(self, name, value, attrs=None):
        html = super(HRBSFormField, self).render(name, value, attrs)
        el_id = self.build_attrs(attrs).get('id')
        html += self.trigger_picker(el_id)
        return mark_safe(html)

    def trigger_picker(self, el_id):
        str = """
        <script>
            $(function(){
                $('#%s').datepicker({
                    format: 'yyyy-mm-dd',
                    onClose: function() {
                        $(this).change(); // Forces re-validation
                    }
                });
            });
        </script>""" % (el_id)
        return str

    media = property(_media)