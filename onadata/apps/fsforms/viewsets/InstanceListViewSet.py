from rest_framework import pagination, permissions
from rest_framework.viewsets import ModelViewSet

from onadata.libs.serializers.data_serializer import DataInstanceSerializer
from onadata.apps.fieldsight.models import Project

from onadata.apps.logger.models import Instance


class ProjectManagerPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        field_sight_form = request.query_params.get('field_sight_form', None)
        project = Project.objects.get(project_forms__pk=field_sight_form)
        project_roles = project.project_roles.all().values('user__username', 'group__name')
        # try:
        #     current_user_role = request.user.user_roles.values('user__username', 'group__name')[0]
        #     if current_user_role['group__name'] == 'Project Manager' and current_user_role in project_roles:
        #         return True
        #     else:
        #         return False
        # except:
        #     pass
        try:
            current_user_role = request.user.user_roles.values('user__username', 'group__name')
            for role in current_user_role:
                if role['group__name'] == 'Project Manager' and role in project_roles:
                    return True
                else:
                    return False
        except:
            pass


class ItemSetPagination(pagination.PageNumberPagination):
    page_size = 200


class InstanceListViewSet(ModelViewSet):
    permission_classes = (ProjectManagerPermission,)
    pagination_class = ItemSetPagination
    serializer_class = DataInstanceSerializer
    queryset = Instance.objects.all()

    def filter_queryset(self, queryset, view=None):
        field_sight_form = self.request.query_params.get('field_sight_form', None)
        instances = Instance.objects.filter(fieldsight_instance__project_fxf=field_sight_form)

        return instances
