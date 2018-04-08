from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
# Create your models here.

STAFF_TYPES = (
        (1, 'Laborer'),
        (2, 'Worker'),
        (3, 'Transporter'),
    )

class Team(models.Model):
    leader = models.ForeignKey(User, related_name="team_leader")
    name = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(User, related_name="team_created_by")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
       return self.name +" C="+ str(self.created_date) +" U="+ str(self.updated_date)

class Staff(models.Model):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    type = models.IntegerField(default=0, choices=STAFF_TYPES)
    team = models.ForeignKey(Team, blank=True, null=True, related_name="staff_team")
    created_by = models.ForeignKey(User, related_name="staff_created_by")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    logs = GenericRelation('eventlog.FieldSightLog')

    def __unicode__(self):
        return self.full_name


class Attendance(models.Model):
    attendance_date = models.DateTimeField()
    staffs = models.ManyToManyField(Staff, null=True, blank=True)
    team = models.ForeignKey(Team, blank=True, null=True, related_name="attandence_team")
    submitted_by = models.ForeignKey(User, related_name="attendance_submitted_by")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    logs = GenericRelation('eventlog.FieldSightLog')

    def __unicode__(self):
        return self.attendance_date