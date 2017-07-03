from django.contrib.auth.models import Group
from django.db import transaction
from fcm.utils import get_device_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, BasePermission

from onadata.apps.fieldsight.mixins import USURPERS
from onadata.apps.fieldsight.models import Site, Project
from onadata.apps.userrole.serializers.UserRoleSerializer import UserRoleSerializer
from onadata.apps.userrole.models import UserRole

SAFE_METHODS = ('GET', 'POST')


class ManagePeoplePermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.role.group.name == "Super Admin":
            return True
        if not request.role.group.name in USURPERS['Reviewer']:
            return False
        return request.role.organization == obj.organization


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.filter(organization__isnull=False, ended_at__isnull=True)
    serializer_class = UserRoleSerializer
    permission_classes = (IsAuthenticated, ManagePeoplePermission)

    def filter_queryset(self, queryset):
        try:
            level = self.kwargs.get('level', None)
            pk = self.kwargs.get('pk', None)
            if level == "0":
                queryset = queryset.filter(site__id=pk, group__name__in=['Site Supervisor', 'Reviewer'])
            elif level == "1":
                queryset = queryset.filter(project__id=pk, group__name='Project Manager')
            elif level == "2":
                queryset = queryset.filter(organization__id=pk, group__name='Organization Admin')
        except:
            queryset = []
        return queryset

    def custom_create(self, * args, **kwargs):
        data = self.request.data
        level = self.kwargs.get('level')
        try:
            with transaction.atomic():
                group = Group.objects.get(name=data.get('group'))
                for user in data.get('users'):
                    if level == "0":
                        site = Site.objects.get(pk=self.kwargs.get('pk'))
                        role, created = UserRole.objects.get_or_create(user_id=user, site_id=site.id,
                                                                       project__id=site.project.id, group=group)
                        Device = get_device_model()
                        if Device.objects.filter(name=role.user.email).exists():
                            message = {'notify_type':'Assign Site', 'site':{'name': site.name, 'id': site.id}}
                            Device.objects.filter(name=role.user.email).send_message(message)

                    elif level == "1":
                        project = Project.objects.get(pk=self.kwargs.get('pk'))
                        role, created = UserRole.objects.get_or_create(user_id=user, project_id=self.kwargs.get('pk'),
                                                                       organization__id=project.organization.id, group=group)
                    elif level =="2":
                        role, created = UserRole.objects.get_or_create(user_id=user,
                                                                       organization_id=self.kwargs.get('pk'), group=group)
                    if not created:
                        role.ended_at = None
                        role.save()
                        role.logs.create(source=self.request.user, type=
                        0, title="new User",
                                            description="new user {0} created by {1}".
                                            format(user.username, self.request.user.username))
        except Exception as e:
            raise ValidationError({
                "User Creation Failed ",
            })
        return Response({'msg': 'ok'}, status=status.HTTP_200_OK)



