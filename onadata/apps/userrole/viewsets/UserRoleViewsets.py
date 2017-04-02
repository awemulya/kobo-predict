from django.contrib.auth.models import Group
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, BasePermission

from onadata.apps.fieldsight.mixins import USURPERS
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
            elif level =="1":
                queryset = queryset.filter(project__id=pk, group__name='Project Manager')
        except:
            queryset = []
        return queryset

    def custom_create(self, * args, **kwargs):
        data = self.request.data
        level = self.kwargs.get('level')
        try:
            with transaction.atomic():
                if level == "0":
                    group = Group.objects.get(name=data.get('group'))
                    for user in data.get('users'):
                        role, created = UserRole.objects.get_or_create(user_id=user, site_id=self.kwargs.get('pk'), group=group)
                        if not created:
                            role.ended_at = None
                            role.save()
                            role.save()
        except:
            raise ValidationError({
                "User Creation Failed ",
            })
        return Response({'msg': 'ok'}, status=status.HTTP_200_OK)



