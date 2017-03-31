from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, BasePermission

from onadata.apps.fieldsight.mixins import USURPERS
from onadata.apps.userrole.serializers.UserRoleSerializer import UserRoleSerializer
from onadata.apps.users.models import User
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


