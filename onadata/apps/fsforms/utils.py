from fcm.utils import get_device_model
from onadata.apps.fieldsight.templatetags.filters import FORM_STATUS

from onadata.apps.userrole.models import UserRole

FIELDSIGHT_XFORM_ID = u"_fieldsight_xform_id"


def send_message(fxf, status=None, comment=None, comment_url=None):
    roles = UserRole.objects.filter(site=fxf.site, ended_at=None, group__name="Site Supervisor")
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
               'comment_url': comment_url,
               'site': {'name': fxf.site.name, 'id': fxf.site.id}}
    Device.objects.filter(name__in=emails).send_message(message)


def send_message_project_form(fxf, status=None, comment=None, comment_url=None):
    roles = UserRole.objects.filter(site__project=fxf.project, ended_at=None, group__name="Site Supervisor").distinct('user')
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    is_delete = False
    status_message = "New Form"
    if fxf.is_deployed:
        status_message = "New Form Deployed"
    else:
        status_message = "Form Undeployed"
    message = {'notify_type': 'ProjectForm',
               'is_delete':is_delete,
               'form_id': fxf.id,
               'comment': comment,
               'form_name': fxf.xf.title,
               'xfid': fxf.xf.id_string,
               'form_type':fxf.form_type(), 'form_type_id':fxf.form_type_id(),
               'status': status_message,
               'comment_url': comment_url,
               'site': {},
               'project': {'name': fxf.project.name, 'id': fxf.project.id}}
    print(message)
    Device.objects.filter(name__in=emails).send_message(message)

def send_message_flagged(fi=None, comment=None, comment_url=None):
    if fi.submitted_by:
        emails = [fi.submitted_by.email]
    Device = get_device_model()
    is_delete = False
    message = {'notify_type': 'Form',
               'is_delete':is_delete,
               'form_id': fi.fsxf.id,
               'project_form_id': fi.fsxf.id,
               'comment': comment,
               'form_name': fi.fsxf.xf.title,
               'xfid': fi.fsxf.xf.id_string,
               'form_type':fi.fsxf.form_type(), 'form_type_id':fi.fsxf.form_type_id(),
               'status': FORM_STATUS.get(fi.form_status,"New Form"),
               'comment_url': comment_url}
    if fi.site:
        message['site'] = {'name': fi.site.name, 'id': fi.site.id}
    if fi.project:
        message['project'] = {'name': fi.project.name, 'id': fi.project.id}
    Device.objects.filter(name__in=emails).send_message(message)

def send_bulk_message_stages(site_ids):
    return
    roles = UserRole.objects.filter(site_id__in=site_ids, ended_at=None, group__name="Site Supervisor").distinct('user')
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'Stages Ready',
               'is_delete':True,
               'site':{'name': site.name, 'id': site.id}}
    Device.objects.filter(name__in=emails).send_message(message)

def send_message_stages(site):
    roles = UserRole.objects.filter(site=site, ended_at=None, group__name="Site Supervisor")
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'Stages Ready',
               'is_delete':True,
               'site':{'name': site.name, 'id': site.id}}
    Device.objects.filter(name__in=emails).send_message(message)


def send_bulk_message_stages_deployed_project(project):
    roles = UserRole.objects.filter(site__project=project, ended_at=None, group__name="Site Supervisor").distinct('user')
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'deploy_all',
               'is_delete':True,
               'is_project':1,
               'description':"Stages Ready in Project {}".format(project.name),
               'project':{'name': project.name, 'id': project.id}}
    Device.objects.filter(name__in=emails).send_message(message)


def send_bulk_message_stages_deployed_site(site):
    roles = UserRole.objects.filter(site=site, ended_at=None, group__name="Site Supervisor")
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'deploy_all',
               'is_delete':True,
               'is_project':0,
               'description':"Stages Ready in Site {}".format(site.name),
               'site':{'name': site.name, 'id': site.id}}
    Device.objects.filter(name__in=emails).send_message(message)


def send_bulk_message_stage_deployed_project(project, main_stage, deploy_id):
    roles = UserRole.objects.filter(site__project=project, ended_at=None, group__name="Site Supervisor").distinct('user')
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'deploy_ms',
               'is_delete':True,
               'is_project':1,
               'deploy_id':deploy_id,
               'description':"Main Stage Ready in Project {}".format(project.name),
               'project':{'name': project.name, 'id': project.id}}
    Device.objects.filter(name__in=emails).send_message(message)


def send_bulk_message_stage_deployed_site(site, main_stage, deploy_id):
    roles = UserRole.objects.filter(site=site, ended_at=None, group__name="Site Supervisor")
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'deploy_ms',
               'is_delete':True,
               'is_project':0,
               'deploy_id':deploy_id,
               'description':"Main Stage Ready in Site {}".format(site.name),
               'site':{'name': site.name, 'id': site.id}}
    Device.objects.filter(name__in=emails).send_message(message)


def send_sub_stage_deployed_project(project, sub_stage, deploy_id):
    roles = UserRole.objects.filter(site__project=project, ended_at=None, group__name="Site Supervisor").distinct('user')
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'deploy_ss',
               'is_delete':True,
               'is_project':1,
               'deploy_id':deploy_id,
               'description':"Sub Stage Ready in Project {}".format(project.name),
               'project':{'name': project.name, 'id': project.id}}
    Device.objects.filter(name__in=emails).send_message(message)


def send_sub_stage_deployed_site(site, sub_stage, deploy_id):
    roles = UserRole.objects.filter(site=site, ended_at=None, group__name="Site Supervisor").distinct('user')
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'deploy_ss',
               'is_delete':True,
               'is_project':0,
               'deploy_id':deploy_id,
               'description':"Sub Stage Ready in Site {}".format(site.name),
               'site':{'name': site.name, 'id': site.id}}
    Device.objects.filter(name__in=emails).send_message(message)



def send_message_un_deploy(fxf):
    roles = UserRole.objects.filter(site=fxf.site, ended_at=None, group__name="Site Supervisor").distinct('user')
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


def send_message_un_deploy_project(fxf):
    roles = UserRole.objects.filter(site__project=fxf.project, ended_at=None, group__name="Site Supervisor").distinct('user')
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'Form Altered Project',
               'is_delete':False,
               'form_id': fxf.id,
               'is_deployed': fxf.is_deployed,
               'form_name': fxf.xf.title,
               'xfid': fxf.xf.id_string,
               'form_type':fxf.form_type(), 'form_type_id':fxf.form_type_id(),
               'site': {},
               'project': {'name': fxf.project.name, 'id': fxf.project.id}}
    Device.objects.filter(name__in=emails).send_message(message)


def send_message_xf_changed(fxf=None, form_type=None, id=None):
    roles = UserRole.objects.filter(site=fxf.site, ended_at=None, group__name="Site Supervisor").distinct('user')
    emails = [r.user.email for r in roles]
    Device = get_device_model()
    message = {'notify_type': 'Kobo Form Changed',
               'is_delete': True,
               'site':{'name': fxf.site.name, 'id': fxf.site.id},
               'form':{'xfid': fxf.xf.id_string, 'form_id': fxf.id,
                       'form_type':form_type,'form_source_id':id,'form_name':fxf.xf.title}}
    Device.objects.filter(name__in=emails).send_message(message)