from fcm.utils import get_device_model
from onadata.apps.fieldsight.templatetags.filters import FORM_STATUS

from onadata.apps.userrole.models import UserRole

FIELDSIGHT_XFORM_ID = u"_fieldsight_xform_id"


def send_message(fsxf, status=None, comment=None):
    roles = UserRole.objects.filter(site=fsxf.site)
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    is_delete = True if status is None and fsxf.fsform is not None else False
    message = {'notify_type': 'Form',
               'is_delete':is_delete,
               'form_id': fsxf.id,
               'comment': comment,
               'form_name': fsxf.xf.title,
               'xfid': fsxf.xf.id_string,
               'form_type':fsxf.form_type(), 'form_type_id':fsxf.form_type_id(),
               'status': FORM_STATUS.get(status,"New Form"),
               'site':{'name': fsxf.site.name, 'id': fsxf.site.id}}
    Device.objects.filter(name__in=emails).send_message(message)


def send_message_stages(site):
    roles = UserRole.objects.filter(site=site)
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'Stages Ready',
               'is_delete':True,
               'site':{'name': site.name, 'id': site.id}}
    Device.objects.filter(name__in=emails).send_message(message)


def send_message_xf_changed(fsxf=None, form_type=None, id=None):
    roles = UserRole.objects.filter(site=fsxf.site)
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'Kobo Form Changed',
               'is_delete': True,
               'site':{'name': fsxf.site.name, 'id': fsxf.site.id},
               'form':{'xfid': fsxf.xf.id_string, 'form_id': fsxf.id,
                       'form_type':form_type,'form_source_id':id,'form_name':fsxf.xf.title}}
    Device.objects.filter(name__in=emails).send_message(message)