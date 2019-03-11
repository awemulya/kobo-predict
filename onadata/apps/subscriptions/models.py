from django.db import models
from django.contrib.auth.models import User


PLAN_CHOICES = (
    (0, 'Free'),
    (1, 'Basic Monthly'),
    (2, 'Basic Yearly'),
    (3, 'Extended Monthly'),
    (4, 'Extended Yearly'),
    (5, 'Pro Monthly'),
    (6, 'Pro Yearly'),
    (7, 'Scale Monthly'),
    (8, 'Scale Yearly')

)


class Customer(models.Model):
    user = models.OneToOneField(User, related_name="customer")
    stripe_cust_id = models.CharField(max_length=300)


class Subscription(models.Model):
    stripe_sub_id = models.CharField(max_length=300)
    stripe_customer = models.ForeignKey(Customer, related_name="subscriptions", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    initiated_on = models.DateTimeField()
    terminated_on = models.DateTimeField(null=True, blank=True)
    plan = models.CharField(choices=PLAN_CHOICES, max_length=300, default=0)