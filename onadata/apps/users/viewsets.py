from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.exceptions import ValidationError

from onadata.apps.fieldsight.mixins import USURPERS
from onadata.apps.users.models import User, UserProfile
from onadata.apps.users.serializers import UserSerializer

SAFE_METHODS = ('GET', 'POST')


class AddPeoplePermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.role.group.name == "Super Admin":
            return True
        if not request.role.group.name in USURPERS['Reviewer']:
            return False
        return request.role.organization == obj.organization


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, AddPeoplePermission)

    def filter_queryset(self, queryset):
        try:
            pk = self.kwargs.get('pk', None)
            queryset = queryset.filter(user_profile__organization__id=pk)
        except:
            queryset = []
        return queryset

    def perform_create(self, serializer):
        data = self.request.data

        if "id" in data and data.get('id'):
            raise ValidationError({
                "Update User Invalid Operation ",
            })

        if "password" not in data:
            raise ValidationError({
                "Password Required ",
            })
        if "cpassword" not in data:
            raise ValidationError({
                "Password Required ",
            })

        if data.get('cpassword') != data.get('password'):
            raise ValidationError({
                "Password Missmatch ",
            })
        username = data.get('username')
        email = data.get('email')
        if User.objects.filter(username=username).exists():
            raise ValidationError({
                "Username Already Used ",
            })
        if User.objects.filter(email=email).exists():
            raise ValidationError({
                "Username Already Used ",
            })
        try:
            with transaction.atomic():
                user = serializer.save()
                user.set_password(data.get('password'))
                user.save()
                UserProfile.objects.create(user=user, organization_id=self.kwargs.get('pk'))
        except:
            raise ValidationError({
                "User Creation Failed ",
            })


