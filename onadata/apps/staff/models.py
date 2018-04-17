import datetime
import json
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
# Create your models here.

STAFF_TYPES = (
        (1, 'TSC Agent'),
        (2, 'Social Mobilizer'),
        (3, 'Junior Builder-Trainer'),
        (4, 'Junior Builder-Trainer'),
    )


GENDER_TYPES = (
        (1, 'Male'),
        (2, 'Female'),
        (3, 'Other'),
    )


class Bank(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
       return self.name

class StaffProject(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(User, related_name="staff_project_created_by")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __unicode__(self):
       return self.name +" C="+ str(self.created_date) +" U="+ str(self.updated_date)

class Team(models.Model):
    leader = models.ForeignKey(User, related_name="team_leader")
    staffproject = models.ForeignKey(StaffProject, related_name="team_project",
     blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(User, related_name="team_created_by")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __unicode__(self):
       return self.name +" C="+ str(self.created_date) +" U="+ str(self.updated_date)

class Staff(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    gender = models.IntegerField(default=1, choices=GENDER_TYPES)
    ethnicity = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to="staffs", default="/static/images/default_user.png")
    designation = models.IntegerField(default=1, choices=STAFF_TYPES)
    team = models.ForeignKey(Team, blank=True, null=True, related_name="staff_team")
    created_by = models.ForeignKey(User, related_name="staff_created_by")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    bank = models.ForeignKey(Bank, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    contract_start = models.DateField(blank=True, null=True)
    contract_end = models.DateField(blank=True, null=True)
    logs = GenericRelation('eventlog.FieldSightLog')
    is_deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.first_name) +" "+  str(self.last_name)

    def get_attendance(self):
        present = Attendance.objects.filter(staffs__in = [self], team_id=self.team_id)
        
        present_list=[]

        for day in present:
            start=int(day.attendance_date.strftime("%s")) * 1000
            day={"id":str(day.id), "start":str(start), "end":str(start), "title":"Present. Attendance submitted by "+day.submitted_by.first_name+" "+day.submitted_by.first_name+".", "class":"event-present"}
            present_list.append(day)
        return json.dumps(present_list)

class Attendance(models.Model):
    attendance_date = models.DateField()
    staffs = models.ManyToManyField(Staff, null=True, blank=True )
    team = models.ForeignKey(Team, blank=True, null=True, related_name="attandence_team")
    submitted_by = models.ForeignKey(User, related_name="attendance_submitted_by")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    logs = GenericRelation('eventlog.FieldSightLog')

    class Meta:
        unique_together = [('attendance_date', 'team'),]

    def __unicode__(self):
        return str(self.attendance_date)