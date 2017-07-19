from django.utils import timezone
from fcm.utils import get_device_model
from django.http import HttpResponseRedirect, JsonResponse
from channels import Group as ChannelGroup
import json

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView
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
    def form_valid(self, form):
        self.object = form.save()
        noti = self.object.logs.create(source=self.request.user, type=6, title="new Role",
                                       organization=self.object.role.organization,
                                       description="new role {0} created by {1}".
                                       format(self.object.name, self.request.user.username))
        result = {}
        result['description'] = 'new role {0} created by {1}'.format(self.object.name, self.request.user.username)
        result['url'] = noti.get_absolute_url()
        ChannelGroup("notify-{}".format(self.object.organization.id)).send({"text": json.dumps(result)})
        ChannelGroup("notify-0").send({"text": json.dumps(result)})

        return HttpResponseRedirect(self.get_success_url())


class UserRoleUpdateView(LoginRequiredMixin, SuperAdminMixin, UserRoleView, UpdateView):
    def form_valid(self, form):
        self.object = form.save()
        noti = self.object.logs.create(source=self.request.user, type=6, title="new Role",
                                       organization=self.object.role.organization,
                                       description="new role {0} updated by {1}".
                                       format(self.object.name, self.request.user.username))
        result = {}
        result['description'] = 'new role {0} update by {1}'.format(self.object.name, self.request.user.username)
        result['url'] = noti.get_absolute_url()
        ChannelGroup("notify-{}".format(self.object.organization.id)).send({"text": json.dumps(result)})
        ChannelGroup("notify-0").send({"text": json.dumps(result)})

        return HttpResponseRedirect(self.get_success_url())


class UserRoleDeleteView(LoginRequiredMixin, SuperAdminMixin, UserRoleView, DeleteView):
    def delete(self,*args, **kwargs):
        self.object = self.get_object()
        noti = self.object.logs.create(source=self.request.user, type=6, title="new Site",
                                       organization=self.object.project.organization,
                                       description="new role {0} deleted by {1}".
                                       format(self.object.name, self.request.user.username))
        result = {}

        result['description'] = 'new role {0} deleted by {1}'.format(self.object.name, self.request.user.username)

        result['url'] = noti.get_absolute_url()
        ChannelGroup("notify-{}".format(self.object.project.organization.id)).send({"text": json.dumps(result)})
        ChannelGroup("notify-0").send({"text": json.dumps(result)})
        return HttpResponseRedirect(self.get_success_url())



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
        if role.group.name == "Site Supervisor":
            Device = get_device_model()
            if Device.objects.filter(name=role.user.email).exists():
                message = {'notify_type':'UnAssign Site', 'site':{'name': role.site.name, 'id': role.site.id}}
                Device.objects.filter(name=role.user.email).send_message(message)
        # serializer = UserRoleSerializer(role)
        return Response({'role':role.id,'role_name':role.group.name, 'msg':"Sucessfully Unassigned {}".format(role.user.username)}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error':e.message}, status=status.HTTP_400_BAD_REQUEST)


