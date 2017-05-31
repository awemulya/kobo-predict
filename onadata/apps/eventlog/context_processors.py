from onadata.apps.eventlog.models import FieldSightLog


def events(request):
    logs = []
    if request.group is not None:
        if request.group.name == "Super Admin":
           logs = FieldSightLog.objects.all()[:10]
        elif request.group.name == "Organization Admin":
            logs = FieldSightLog.objects.filter(organization=request.organization)[:10]
        elif request.group.name in ["Project Manager", "Reviewer"]:
            logs = FieldSightLog.objects.filter(organization=request.organization)[:10]
    return {
        'notifications': logs,
        'fieldsight_message': []

    }