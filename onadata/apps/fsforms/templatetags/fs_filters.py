# -*- coding: utf-8 -*-

from django.template import Library

from onadata.apps.fsforms.models import FieldSightFormLibrary

register = Library()


@register.filter
def library(xf_id):
    if not FieldSightFormLibrary.objects.filter(xf__id_string=xf_id).exists():
        return 5
    form = FieldSightFormLibrary.objects.get(xf__id_string=xf_id)
    if form.is_global:
        return  0
    elif form.project:
        return 2
    return 1
