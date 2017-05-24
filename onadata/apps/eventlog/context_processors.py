from onadata.apps.eventlog.models import FieldSightLog


def events(request):
    return {
        'notifications': FieldSightLog.objects.all()[:10]

    }