from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import ListView
from rest_framework.response import Response

from onadata.apps.fieldsight.mixins import (LoginRequiredMixin, SuperAdminMixin, CreateView, UpdateView, DeleteView,
                                            AjaxableResponseMixinUser)
from onadata.apps.userrole.serializers.UserRoleSerializer import UserRoleSerializer
from onadata.apps.userrole.viewsets.UserRoleViewsets import ManagePeoplePermission
from .forms import UserRoleForm, UserForm
from .models import UserRole as Role, UserRole


def set_role(request, pk):
    role = Role.objects.get(pk=pk, user=request.user)
    if role:
        request.session['role'] = role.pk
    return redirect(request.META.get('HTTP_REFERER', '/'))


class UserRoleView(object):
    model = UserRole
    # get sucess url dynamacially according to who is creating people(roles)
    success_url = reverse_lazy('role:user-role-list')
    form_class = UserRoleForm


class UserRoleListView(LoginRequiredMixin, SuperAdminMixin, UserRoleView, ListView):
    pass


class UserRoleCreateView(LoginRequiredMixin, SuperAdminMixin, UserRoleView, CreateView):
    pass


class UserRoleUpdateView(LoginRequiredMixin, SuperAdminMixin, UserRoleView, UpdateView):
    pass


class UserRoleDeleteView(LoginRequiredMixin, SuperAdminMixin, UserRoleView, DeleteView):
    pass


class UserView(object):
    model = User
    success_url = reverse_lazy('fieldsight:user-list')
    form_class = UserForm


class UserCreate(LoginRequiredMixin, AjaxableResponseMixinUser, UserView, CreateView):
    def get_template_names(self):
        return ['users/create_user.html']


@api_view(['POST'])
@permission_classes([ManagePeoplePermission])
def remove_role(request):
    try:
        role = UserRole.objects.get(pk=request.data.get("id"))
        role.ended_at = timezone.now()
        role.save()
        serializer = UserRoleSerializer(role)
        return Response({'role':role.id,'role_name':role.group.name, 'msg':"Sucessfully Unassigned {}".format(role.user.username)}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error':e.message}, status=status.HTTP_400_BAD_REQUEST)


