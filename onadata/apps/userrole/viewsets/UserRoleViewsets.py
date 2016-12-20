from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from onadata.apps.userrole.serializers.UserRoleSerializer import UserRoleSerializer
from onadata.apps.userrole.models import UserRole


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all().distinct('user')
    serializer_class = UserRoleSerializer
    permission_classes = (IsAuthenticated,)


