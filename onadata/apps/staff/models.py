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


class Team(models.Model):
    leader = models.ForeignKey(User, related_name="team_leader")
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
    gender = models.IntegerField(default=1, choices=GENDER_TYPES)
    ethnicity = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to="staffs", default="staffs/default_staff_image.jpg")
    designation = models.IntegerField(default=1, choices=STAFF_TYPES)
    team = models.ForeignKey(Team, blank=True, null=True, related_name="staff_team")
    created_by = models.ForeignKey(User, related_name="staff_created_by")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    bank = models.ForeignKey(Bank, blank=True, null=True)
    contract_start = models.DateField(blank=True, null=True)
    contract_end = models.DateField(blank=True, null=True)
    logs = GenericRelation('eventlog.FieldSightLog')
    is_deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.first_name +" "+  self.last_name


class Attendance(models.Model):
    attendance_date = models.DateTimeField()
    staffs = models.ManyToManyField(Staff, null=True, blank=True)
    team = models.ForeignKey(Team, blank=True, null=True, related_name="attandence_team")
    submitted_by = models.ForeignKey(User, related_name="attendance_submitted_by")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    logs = GenericRelation('eventlog.FieldSightLog')

    def __unicode__(self):
        return self.attendance_date