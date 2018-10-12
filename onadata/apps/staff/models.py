import datetime
import json
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import PermissionDenied
# Create your models here.

STAFF_TYPES = (
        (1, 'TSC Agent'),
        (2, 'Social Mobilizer'),
        (3, 'Senior Builder-Trainer'),
        (4, 'Junior Builder-Trainer'),
        (5, 'Team Leader'),
        (6, 'Support Staff'), 
        (7, 'Field Supervisor'),
        (8, 'Community Messenger'),  
    )

STAFF_TYPES_SHORT = (
        (1, 'TSC A'),
        (2, 'S M'),
        (3, 'Sr. B-T'),
        (4, 'Jr. B-T'),
        (5, 'TL'),
        (6, 'SS'),
        (7, 'FS'),
        (8, 'CM'),
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

    def get_attendance(self):
        days = self.attandence_team.all()
        
        present_list=[]

        for day in days:
            start=int(day.attendance_date.strftime("%s")) * 1000
            
            for staff in day.staffs.all():
                record={"id":str(day.id)+"-"+str(staff.id), "start":str(start), "end":str(start), "title":staff.get_fullname()+" Present. Attendance submitted by "+day.submitted_by.first_name+" "+day.submitted_by.first_name+".", "class":"event-present"}
                present_list.append(record)
        return json.dumps(present_list)

    def get_attendance_for_excel(self, year, month):
        days = self.attandence_team.filter(attendance_date__year=year, attendance_date__month=month)
        attendances={}
        for day in days:
            attendances[str(day.attendance_date)] = day.staffs.all().values_list('id', flat=True)
        return attendances


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
    bank = models.ForeignKey(Bank, blank=True, null=True, default=None)
    date_of_birth = models.DateField(blank=True, null=True)
    contract_start = models.DateField(blank=True, null=True)
    contract_end = models.DateField(blank=True, null=True)
    logs = GenericRelation('eventlog.FieldSightLog')
    is_deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.first_name) +" "+  str(self.last_name)

    def get_designation(self):
        return dict(STAFF_TYPES)[self.designation]

    def get_abr_designation(self):
        return dict(STAFF_TYPES_SHORT)[self.designation]

    def get_fullname(self):
        return str(self.first_name) +" "+ str(self.last_name)

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
    staffs = models.ManyToManyField(Staff)
    team = models.ForeignKey(Team, blank=True, null=True, related_name="attandence_team")
    submitted_by = models.ForeignKey(User, related_name="attendance_submitted_by")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    logs = GenericRelation('eventlog.FieldSightLog')

    class Meta:
        unique_together = [('attendance_date', 'team', 'is_deleted'),]

    def save(self, *args, **kwargs):
        attendance_date = datetime.datetime.strptime(str(self.attendance_date), '%Y-%m-%d')
        if attendance_date > datetime.datetime.today():
            raise PermissionDenied()
        else:
            super(Attendance, self).save(*args, **kwargs)  # Call the "real" save() method.
    

    def __unicode__(self):
        return str(self.attendance_date)