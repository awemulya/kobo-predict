from django.conf import settings

from onadata.apps.fsforms.models import FieldSightXF


class Entry:
    def __init__(self, status=0, submission_time=None, submitted_by=None, fsid=None, instance=None):
        self.status = status
        self.submission_time = submission_time
        self.submitted_by = submitted_by
        self.fsid = fsid
        self.instance = instance
        self.fsform = None
        if FieldSightXF.objects.get(pk=self.fsid):
            self.fsform = FieldSightXF.objects.get(pk=self.fsid)


class Submission():
    @classmethod
    def get_site_submission(cls, site):
        query = {'fs_site': str(site)}
        fields = {'fs_status':1, '_submission_time':1, '_submitted_by':1, 'fs_uuid':1, '_id':0}
        cursor =  settings.MONGO_DB.instances.find(query)
        outstanding, flagged, approved, rejected = [], [], [], []
        if cursor.count():
            data = list(cursor)
            for form in data:
                entry = Entry(form['fs_status'],
                              form['_submission_time'],
                              form['_submitted_by'],
                              form['fs_uuid'],
                              form['_id'])
                if entry.status == 0:
                    outstanding.append(entry)
                elif entry.status == 1:
                    rejected.append(entry)
                elif entry.status == 2:
                    flagged.append(entry)
                else:
                    approved.append(entry)
        return outstanding, flagged, approved, rejected

