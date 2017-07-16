from django.conf import settings

from onadata.apps.eventlog.models import FieldSightLog, FieldSightMessage


def events(request):
    logs = []
    messages = FieldSightMessage.inbox(request.user)
    oid = 0
    if request.group is not None:
        if request.group.name == "Super Admin":
           logs = FieldSightLog.objects.filter(is_seen=False)[:10]
        elif request.group.name == "Organization Admin":
            logs = FieldSightLog.objects.filter(organization=request.organization).filter(is_seen=False)[:10]
            oid = request.organization.id
        elif request.group.name in ["Project Manager", "Reviewer"]:
            logs = FieldSightLog.objects.filter(organization=request.organization).filter(is_seen=False)[:10]
            oid = request.organization.id
    channels_url = "ws://"+settings.WEBSOCKET_URL+":"+settings.WEBSOCKET_PORT+"/" \
        if settings.WEBSOCKET_PORT else "ws://"+settings.WEBSOCKET_URL+"/"
    return {
        'notifications': logs,
        'fieldsight_message': messages,
        'oid': oid,
        'channels_url': channels_url

    }