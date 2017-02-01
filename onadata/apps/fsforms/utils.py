# fieldsight common tags
from fcm.utils import get_device_model
from onadata.apps.fieldsight.templatetags.filters import FORM_STATUS

from onadata.apps.userrole.models import UserRole

FIELDSIGHT_XFORM_ID = u"_fieldsight_xform_id"


def send_message(fsxf, status=None, comment=None):
    roles = UserRole.objects.filter(site=fsxf.site)
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'Form',
               'form_id': fsxf.id,
               'comment': comment,
               'form_name': fsxf.xf.title,
               'url': 'forms/{}/form.xml'.format(fsxf.id),
               'manifiest': 'forms/{}/{}'.format(fsxf.id, fsxf.site.id),
               'status': FORM_STATUS.get(status,"Outstanding"),
               'site':{'name': fsxf.site.name, 'id': fsxf.site.id}}
    Device.objects.filter(name__in=emails).send_message(message)