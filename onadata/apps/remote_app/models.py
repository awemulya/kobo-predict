from random import choice
from string import ascii_lowercase, digits

from django.utils import timezone
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

import jwt

from onadata.apps.fieldsight.models import Project, Site


def generate_random_username():
    chars = ascii_lowercase + digits
    length = 16
    username = ''.join([choice(chars) for _ in range(length)])
    User = get_user_model()

    try:
        User.objects.get(username=username)
        return generate_random_username()
    except User.DoesNotExist:
        return username


class RemoteApp(models.Model):
    title = models.CharField(max_length=255)
    projects = models.ManyToManyField(
        Project,
        through='ConnectedProject',
        blank=True
    )
    auth_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    token = models.TextField(blank=True)

    def __str__(self):
        return self.title

    def clean(self):
        if not hasattr(self, 'auth_user') or not self.auth_user:
            User = get_user_model()
            user = User.objects.create_user(
                username=generate_random_username()
            )
            self.auth_user = user

        if not hasattr(self, 'token') or not self.token:
            payload = {'userId': self.auth_user.id}
            self.token = jwt.encode(
                payload,
                settings.SECRET_KEY,
                algorithm='HS256',
            )


class ConnectedProject(models.Model):
    key = models.CharField(max_length=255)
    project = models.ForeignKey(Project)
    app = models.ForeignKey(RemoteApp)
    updated_at = models.DateTimeField(default=None, blank=True, null=True)

    def __str__(self):
        return str(self.project)


class ConnectedDomain(models.Model):
    app = models.ForeignKey(RemoteApp)
    domain = models.CharField(max_length=255)

    def __str__(self):
        return self.domain


@receiver(post_delete, sender=RemoteApp)
def handle_remote_app_delete(sender, instance, **kwargs):
    user = instance.auth_user
    user.delete()


@receiver(post_save, sender=Project)
def handle_project_save(sender, instance, **kwargs):
    project = ConnectedProject.objects.filter(
        project=instance
    ).first()
    if project:
        project.updated_at = timezone.now()
        project.save()


@receiver(post_save, sender=Site)
def handle_site_save(sender, instance, **kwargs):
    project = ConnectedProject.objects.filter(
        project=instance.project
    ).first()
    if project:
        project.updated_at = timezone.now()
        project.save()
