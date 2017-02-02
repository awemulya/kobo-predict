from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from onadata.apps.userrole.serializers.UserRoleSerializer import UserRoleSerializer
from onadata.apps.userrole.models import UserRole


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.filter(organization__isnull=False).distinct('user')
    serializer_class = UserRoleSerializer
    permission_classes = (IsAuthenticated,)

    def filter_queryset(self, queryset):
        try:
            org = self.request.user.user_profile.organization
            queryset = queryset.filter(ended_at__isnull=True, organization = org)
        except:
            queryset = []
        return queryset


