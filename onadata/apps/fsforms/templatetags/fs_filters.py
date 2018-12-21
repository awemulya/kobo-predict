# -*- coding: utf-8 -*-

from django.template import Library

from onadata.apps.fieldsight.templatetags.filters import get_site_level
from onadata.apps.fsforms.models import FieldSightFormLibrary, FInstance, FieldSightXF
from onadata.apps.logger.models import XForm

FORM_STATUS = {0: 'Outstanding', 1: 'Rejected', 2: 'Flagged', 3: 'Approved'}
register = Library()


@register.filter
def setkey(key):
    key = key.replace("_0", "")
    key = key.replace("_", " ")
    return key



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


def get_status_level(status=0):
    if not isinstance(status, int):
        return ""
    if not FInstance.objects.filter(instance__id=status).exists():
        return ""
    FORM_STATUS.get(FInstance.objects.get(instance__id=status).form_status, "")


@register.filter
def exceptlast(lst):
    my_list = lst[:-1]
    if isinstance(my_list[-1], list):
        my_list = my_list[:-1]
    my_list[-1] = get_status_level(my_list[-5])
    my_list[-2] = get_site_level(my_list[-2])
    return my_list


@register.filter
def fsmedia(data_list):
    if isinstance(data_list[-1], list):
        return data_list[-1]
    elif isinstance(data_list[-2], list):
        return data_list[-2]
    return []


@register.filter
def project_submissions(formid):
    FIs = FInstance.objects.filter(project_fxf_id = formid).count()
    return FIs


@register.filter
def site_submissions(fsxf, site_id):
    if fsxf.site:
        return FInstance.objects.filter(site_fxf_id= fsxf.id).count()
    else:
        return FInstance.objects.filter(project_fxf_id=fsxf.id, site__id=site_id).count()

@register.filter
def getlatestsubmittiondate(fsxf, site_id):
    if fsxf.site is not None:
        return fsxf.site_form_instances.order_by('-pk').values('date')[:1]
    else:
        return fsxf.project_form_instances.filter(site=site_id).order_by('-pk').values('date')[:1]

@register.filter
def can_edit_finstance(user, finstance):
    # TODO Check for project admins and stuffs?
    return user.has_perm('logger.change_xform', finstance.instance.xform)\

@register.filter
def is_project_val(fsf, is_project):
    return fsf ,is_project


def get_xform_version(xform):
        import re
        p = re.compile('version="(.*)">')
        m = p.search(xform.xml)
        if m:
            return m.group(1)
        return None


@register.filter
def version_submission_data((fsf, is_project), xform_or_history):
    date = ""
    count = 0
    if isinstance(xform_or_history,  XForm):
        form_version = get_xform_version(xform_or_history)
    else:
        form_version = xform_or_history.version
    if is_project == "1":
        latest = FInstance.objects.filter(project_fxf=fsf, version=form_version).last()
        if latest:
            date = latest.date
        count = FInstance.objects.filter(project_fxf=fsf, version=form_version).count()
    has_submissions = True if count > 0 else False
    return dict(date=date, count=count, has_submissions=has_submissions, version=form_version)
