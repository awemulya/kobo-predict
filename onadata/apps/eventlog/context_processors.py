from django.conf import settings

from onadata.apps.eventlog.models import FieldSightLog, FieldSightMessage


def events(request):
    from django.contrib.sites.models import Site
    site = Site.objects.first()
    if request.user.is_anonymous():
        messages = []
    else:
        messages = FieldSightMessage.inbox(request.user)
    oid = 0
    pid = 0
    sid = 0
    logs = []
    if request.group is not None:
        if request.group.name == "Super Admin":
           logs = FieldSightLog.objects.filter(is_seen=False)[:100]
           oid = 0
        elif request.group.name == "Organization Admin":
            logs = FieldSightLog.objects.filter(organization=request.organization).filter(is_seen=False)[:100]
            oid = request.organization.id
        elif request.group.name == "Project Manager":
            logs = FieldSightLog.objects.filter(organization=request.organization).filter(is_seen=False)[:100]
            pid = request.project.id
        elif request.group.name in ["Reviewer", "Site Supevisor"]:
            logs = FieldSightLog.objects.filter(organization=request.organization).filter(is_seen=False)[:100]
            sid = request.site.id
    else:
        logs = []
        oid = None
    channels_url = "ws://"+settings.WEBSOCKET_URL+":"+settings.WEBSOCKET_PORT+"/" \
    if settings.WEBSOCKET_PORT else "ws://"+settings.WEBSOCKET_URL+"/"
    return {
        'notifications': logs,
        'fieldsight_message': messages,
        'oid': oid,
        'pid': pid,
        'sid': sid,
        'channels_url': channels_url,
        'site_name': site.domain

    }