from django.db import transaction
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import detail_route
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from onadata.apps.api.viewsets.xform_viewset import CsrfExemptSessionAuthentication
from onadata.apps.fieldsight.mixins import USURPERS
from onadata.apps.userrole.models import UserRole
from onadata.apps.users.models import User, UserProfile
from onadata.apps.users.serializers import UserSerializer, UserSerializerProfile

SAFE_METHODS = ('GET', 'POST')


class AddPeoplePermission(BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.role.group.name == "Super Admin":
            return True
        # elif request.role.group.name == "Organization Admin":
        #     return obj.user.organization == request.role.organization
        # elif request.role.group.name == "Project Manager":
        #     return not UserRole.objects.filter(user=obj.user, group_name__in=USURPERS["Project"]).exists()
        # elif
        #
        #     return False
        #     return obj.user == request.user
        # return request.role.organization == obj.organization
        return request.role.group.name in USURPERS['Reviewer']


class EditProfilePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.user:
            return True

        elif request.role.group.name == "Super Admin":
            return True

        elif request.role.group.name == "Organization Admin":
            return obj.organization == request.role.organization
        elif request.role.group.name == "Project Manager":
            if UserRole.objects.filter(user=obj.user, group_name__in=USURPERS["Project"]).exists():
                return False
            return obj.user_profile.organization == request.role.organization
        elif request.role.group.name == "Reviewer":
            if UserRole.objects.filter(user=obj.user, group_name__in=USURPERS["Reviewer"]).exists():
                return False
            return obj == request.user
        return False


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
                user.is_superuser = True
                user.save()
                UserProfile.objects.create(user=user, organization_id=self.kwargs.get('pk'))
        except:
            raise ValidationError({
                "User Creation Failed ",
            })


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializerProfile
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated, EditProfilePermission)

    def retrieve(self, request, pk=None):
        queryset = UserProfile.objects.all()
        if pk is not None:
            profile = get_object_or_404(queryset, pk=pk)
        else:
            profile = UserProfile.objects.get(user=request.user)
        serializer = UserSerializerProfile(profile)
        return Response(serializer.data)

    def get_serializer_context(self):
        return {'request': self.request}

