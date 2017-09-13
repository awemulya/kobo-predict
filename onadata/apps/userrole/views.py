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


# class MultiUserAssignRoleViewSet(ListView):
    
  
#     def get(self, request, *args, **kwargs):
#         queryset = UserRole.objects.filter(organization__isnull=False, ended_at__isnull=True)
#         try:
#             level = self.kwargs.get('level', None)
#             pk = self.kwargs.get('pk', None)
#             if level == "0":
#                 user_queryset = queryset.filter(site__id=pk, group__name__in=['Site Supervisor', 'Reviewer'])
#             elif level == "1":
#                 user_queryset = queryset.filter(project__id=pk, group__name='Project Manager')
#             elif level == "2":
#                 user_queryset = queryset.filter(organization__id=pk, group__name='Organization Admin')
#         except:
#             user_queryset = []

#         # try:
#         #     pk = self.kwargs.get('pk', None)
#         #     if level == "1":
#         #         content_queryset = Sites.objects.filter(project__id=pk)
#         #         content = OrganizationSerializer(content_queryset, many=True, context=context)

#         #     elif level == "2":
#         #         content_queryset = Project.objects.filter(organization__id=pk)
#         #         content = ProjectSerializer(content_queryset, many=True, context=context)
#         # except:
#         #     content_queryset = []
        
#         # queryset=[]
#         # queryset[users] = user_queryset
#         # queryset[content] = content_queryset


#         users = UserRoleSerializer(user_queryset)
        

        
#         return queryset

#     def post(self, * args, **kwargs):
#         data = self.request.data
#         level = self.kwargs.get('level')
#         try:
#             with transaction.atomic():
#                 group = Group.objects.get(name=data.get('group'))
#                 if level == "0":
#                     for site_id in data.get('sites'):
#                         site = Site.objects.get(pk=site_id)
#                         for user in data.get('users'):
#                             role, created = UserRole.objects.get_or_create(user_id=user, site_id=site.id,
#                                                                            project__id=site.project.id, group=group)

#                             if created:
#                                 description = "{0} was assigned  as {1} in {2}".format(
#                                     role.user.get_full_name(), role.lgroup.name, role.project)
#                                 noti_type = 8

#                                 if data.get('group') == "Reviewer":
#                                     noti_type =7
                                
#                                 noti = role.logs.create(source=role.user, type=noti_type, title=description,
#                                                         description=description, content_type=site, extra_object=self.request.user,
#                                                         site=role.site)
#                                 result = {}
#                                 result['description'] = description
#                                 result['url'] = noti.get_absolute_url()
#                                 ChannelGroup("notify-{}".format(role.organization.id)).send({"text": json.dumps(result)})
#                                 ChannelGroup("project-{}".format(role.project.id)).send({"text": json.dumps(result)})
#                                 ChannelGroup("site-{}".format(role.site.id)).send({"text": json.dumps(result)})
#                                 ChannelGroup("notify-0").send({"text": json.dumps(result)})

#                             Device = get_device_model()
#                             if Device.objects.filter(name=role.user.email).exists():
#                                 message = {'notify_type':'Assign Site', 'site':{'name': site.name, 'id': site.id}}
#                                 Device.objects.filter(name=role.user.email).send_message(message)

#                 elif level == "1":
#                     for project_id in data.get('projects'):
#                         project = Project.objects.get(pk=project_id)
#                         for user in data.get('users'):
#                             role, created = UserRole.objects.get_or_create(user_id=user, project_id=project_id,
#                                                                            organization__id=project.organization.id,
#                                                                            project__id=project_id,
#                                                                            group=group)
#                             if created:
#                                 description = "{0} was assigned  as Project Manager in {1}".format(
#                                     role.user.get_full_name(), role.project)
#                                 noti = role.logs.create(source=role.user, type=6, title=description, description=description,
#                                  content_type=project, extra_object=self.request.user)
#                                 result = {}
#                                 result['description'] = description
#                                 result['url'] = noti.get_absolute_url()
#                                 ChannelGroup("notify-{}".format(role.organization.id)).send({"text": json.dumps(result)})
#                                 ChannelGroup("project-{}".format(role.project.id)).send({"text": json.dumps(result)})
#                                 ChannelGroup("notify-0").send({"text": json.dumps(result)})
                
#                 elif level =="2":
#                     for organization_id in data.get('organizations'):
#                         organization = Organization.objects.get(pk=organization_id)
#                         for user in data.get('users'):
#                             role, created = UserRole.objects.get_or_create(user_id=user,
#                                                                            organization_id=organization_id, group=group)
#                             if created:
#                                 description = "{0} was assigned  as Organization Admin in {1}".format(
#                                     role.user.get_full_name(), role.organization)
#                                 noti = role.logs.create(source=role.user, type=4, title=description, description=description,
#                                  content_type=organization, extra_object=self.request.user)
#                                 result = {}
#                                 result['description'] = description
#                                 result['url'] = noti.get_absolute_url()
#                                 ChannelGroup("notify-{}".format(role.organization.id)).send({"text": json.dumps(result)})
#                                 ChannelGroup("notify-0").send({"text": json.dumps(result)})
#                             else:
#                                 role.ended_at = None
#                                 role.save()


#         except Exception as e:
#             raise ValidationError({
#                 "User Creation Failed ".format(str(e)),
#             })
#         return Response({'msg': 'ok'}, status=status.HTTP_200_OK)