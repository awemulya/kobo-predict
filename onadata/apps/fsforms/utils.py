from fcm.utils import get_device_model
from onadata.apps.fieldsight.templatetags.filters import FORM_STATUS

from onadata.apps.userrole.models import UserRole

FIELDSIGHT_XFORM_ID = u"_fieldsight_xform_id"


def send_message(fxf, status=None, comment=None, comment_url=None):
    roles = UserRole.objects.filter(site=fxf.site)
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    is_delete = True if status is None and fxf.fsform is not None else False
    message = {'notify_type': 'Form',
               'is_delete':is_delete,
               'form_id': fxf.id,
               'comment': comment,
               'form_name': fxf.xf.title,
               'xfid': fxf.xf.id_string,
               'form_type':fxf.form_type(), 'form_type_id':fxf.form_type_id(),
               'status': FORM_STATUS.get(status,"New Form"),
               '': comment_url,
               'site': {'name': fxf.site.name, 'id': fxf.site.id}}
    Device.objects.filter(name__in=emails).send_message(message)


def send_message_stages(site):
    roles = UserRole.objects.filter(site=site)
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'Stages Ready',
               'is_delete':True,
               'site':{'name': site.name, 'id': site.id}}
    Device.objects.filter(name__in=emails).send_message(message)


def send_message_un_deploy(fxf):
    roles = UserRole.objects.filter(site=fxf.site)
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'Form Altered',
               'is_delete':False,
               'form_id': fxf.id,
                   'is_deployed': fxf.is_deployed,
               'form_name': fxf.xf.title,
               'xfid': fxf.xf.id_string,
               'form_type':fxf.form_type(), 'form_type_id':fxf.form_type_id(),
               'site': {'name': fxf.site.name, 'id': fxf.site.id}}
    Device.objects.filter(name__in=emails).send_message(message)


def send_message_xf_changed(fxf=None, form_type=None, id=None):
    roles = UserRole.objects.filter(site=fxf.site)
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'Kobo Form Changed',
               'is_delete': True,
               'site':{'name': fxf.site.name, 'id': fxf.site.id},
               'form':{'xfid': fxf.xf.id_string, 'form_id': fxf.id,
                       'form_type':form_type,'form_source_id':id,'form_name':fxf.xf.title}}
    Device.objects.filter(name__in=emails).send_message(message)