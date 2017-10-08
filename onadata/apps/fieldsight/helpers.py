from django.http import JsonResponse
from django import forms
from django.utils.safestring import mark_safe


class AdminImageWidget(forms.FileInput):
    """
    A ImageField Widget for admin that shows a thumbnail.
    """

    def __init__(self, attrs={}):
        super(AdminImageWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            output.append(('<img src="%s" id="logo-prev" style="height: 250px;" />'
                           % (value.url)))
        output.append(super(AdminImageWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

def json_from_object(obj):
    data = {
        'id': obj.id
    }

    if hasattr(obj, 'name'):
        data['name'] = obj.name
    elif hasattr(obj, 'address'):
        data['address'] = obj.address
    else:
        data['name'] = str(obj)

    if hasattr(obj, 'phone'):
        data['phone'] = obj.percent
    return JsonResponse(data)
