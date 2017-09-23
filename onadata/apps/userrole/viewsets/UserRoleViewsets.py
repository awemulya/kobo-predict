import json
from django.contrib.auth.models import Group
from django.db import transaction
from fcm.utils import get_device_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, BasePermission

from channels import Group as ChannelGroup
from onadata.apps.fieldsight.mixins import USURPERS
from onadata.apps.fieldsight.models import Site, Project, Organization
from onadata.apps.userrole.serializers.UserRoleSerializer import UserRoleSerializer
from onadata.apps.fieldsight.serializers.ProjectSerializer import ProjectTypeSerializer
from onadata.apps.fieldsight.serializers.SiteSerializer import SiteSerializer
from onadata.apps.userrole.models import UserRole
from django.db.models import Q
from django.views.generic import View
from django.http import HttpResponse
from rest_framework.pagination import PageNumberPagination

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
                queryset = queryset.filter(site__id=pk, group__name__in=['Site Supervisor', 'Reviewer']).distinct('user_id')
            elif level == "1":
                queryset = queryset.filter(project__id=pk, group__name='Project Manager').distinct('user_id')
            elif level == "2":
                queryset = queryset.filter(organization__id=pk, group__name='Organization Admin').distinct('user_id')
        except:
            queryset = []
        return queryset

    def custom_create(self, * args, **kwargs):
        data = self.request.data
        # print "======================================================="
        # print data
        # print data.get('users')
       
        level = self.kwargs.get('level')
        # try:
        with transaction.atomic():
            group = Group.objects.get(name=data.get('group'))
            for user in data.get('users'):
                if level == "0":
                    site = Site.objects.get(pk=self.kwargs.get('pk'))
                    role, created = UserRole.objects.get_or_create(user_id=user, site_id=site.id,
                                                                   project__id=site.project.id, group=group)

                    if created:
                        description = "{0} was assigned  as {1} in {2}".format(
                            role.user.get_full_name(), role.lgroup.name, role.project)
                        noti_type = 8

                        if data.get('group') == "Reviewer":
                            noti_type =7
                        
                        noti = role.logs.create(source=role.user, type=noti_type, title=description,
                                                description=description, content_type=site, extra_object=self.request.user,
                                                site=role.site)
                        result = {}
                        result['description'] = description
                        result['url'] = noti.get_absolute_url()
                        ChannelGroup("notify-{}".format(role.organization.id)).send({"text": json.dumps(result)})
                        ChannelGroup("project-{}".format(role.project.id)).send({"text": json.dumps(result)})
                        ChannelGroup("site-{}".format(role.site.id)).send({"text": json.dumps(result)})
                        ChannelGroup("notify-0").send({"text": json.dumps(result)})

                    Device = get_device_model()
                    if Device.objects.filter(name=role.user.email).exists():
                        message = {'notify_type':'Assign Site', 'site':{'name': site.name, 'id': site.id}}
                        Device.objects.filter(name=role.user.email).send_message(message)

                elif level == "1":
                    project = Project.objects.get(pk=self.kwargs.get('pk'))
                    role, created = UserRole.objects.get_or_create(user_id=user, project_id=self.kwargs.get('pk'),
                                                                   organization__id=project.organization.id,
                                                                   project__id=project.id,
                                                                   group=group)
                    if created:
                        description = "{0} was assigned  as Project Manager in {1}".format(
                            role.user.get_full_name(), role.project)
                        noti = role.logs.create(source=role.user, type=6, title=description, description=description,
                         content_type=project, extra_object=self.request.user)
                        result = {}
                        result['description'] = description
                        result['url'] = noti.get_absolute_url()
                        ChannelGroup("notify-{}".format(role.organization.id)).send({"text": json.dumps(result)})
                        ChannelGroup("project-{}".format(role.project.id)).send({"text": json.dumps(result)})
                        ChannelGroup("notify-0").send({"text": json.dumps(result)})
                elif level =="2":
                    organization = Organization.objects.get(pk=self.kwargs.get('pk'))
                    role, created = UserRole.objects.get_or_create(user_id=user,
                                                                   organization_id=self.kwargs.get('pk'), group=group)
                    if created:
                        description = "{0} was assigned  as Organization Admin in {1}".format(
                            role.user.get_full_name(), role.organization)
                        noti = role.logs.create(source=role.user, type=4, title=description, description=description,
                         content_type=organization, extra_object=self.request.user)
                        result = {}
                        result['description'] = description
                        result['url'] = noti.get_absolute_url()
                        ChannelGroup("notify-{}".format(role.organization.id)).send({"text": json.dumps(result)})
                        ChannelGroup("notify-0").send({"text": json.dumps(result)})
                    else:
                        role.ended_at = None
                        role.save()


        # except Exception as e:
        #     raise ValidationError({
        #         "User Creation Failed ".format(str(e)),
        #     })
        return Response({'msg': data}, status=status.HTTP_200_OK)

    def all_notification(user, message):
        ChannelGroup("%s" % user).send({
            "text": json.dumps({
                "msg": message
            })
        })

class MultiUserAssignRoleViewSet(View):
    def get(self, * args, **kwargs):
        return HttpResponse('Get Request Not Allowed.')

    def post(self, * args, **kwargs):
        queryset = UserRole.objects.filter(organization__isnull=False, ended_at__isnull=True)
        data = self.request.data
        level = self.kwargs.get('level')
        try:
            with transaction.atomic():
                group = Group.objects.get(name=data.get('group'))
                if level == "0":
                    for site_id in data.get('sites'):
                        site = Site.objects.get(pk=site_id)
                        for user in data.get('users'):
                            role, created = UserRole.objects.get_or_create(user_id=user, site_id=site.id,
                                                                           project__id=site.project.id, organization_id=site.project.organization.id, group=group)
                            if created:
                                description = "{0} was assigned  as {1} in {2}".format(
                                    role.user.get_full_name(), role.lgroup.name, role.project)
                                noti_type = 8

                                if data.get('group') == "Reviewer":
                                    noti_type =7
                                
                                noti = role.logs.create(source=role.user, type=noti_type, title=description,
                                                        description=description, content_type=site, extra_object=self.request.user,
                                                        site=role.site)
                                result = {}
                                result['description'] = description
                                result['url'] = noti.get_absolute_url()
                                ChannelGroup("notify-{}".format(role.organization.id)).send({"text": json.dumps(result)})
                                ChannelGroup("project-{}".format(role.project.id)).send({"text": json.dumps(result)})
                                ChannelGroup("site-{}".format(role.site.id)).send({"text": json.dumps(result)})
                                ChannelGroup("notify-0").send({"text": json.dumps(result)})

                            Device = get_device_model()
                            if Device.objects.filter(name=role.user.email).exists():
                                message = {'notify_type':'Assign Site', 'site':{'name': site.name, 'id': site.id}}
                                Device.objects.filter(name=role.user.email).send_message(message)

                elif level == "1":
                    for project_id in data.get('projects'):
                        project = Project.objects.get(pk=project_id)
                        for user in data.get('users'):
                            role, created = UserRole.objects.get_or_create(user_id=user, project_id=project_id,
                                                                           organization__id=project.organization.id,
                                                                           group=group)
                            if created:
                                description = "{0} was assigned  as Project Manager in {1}".format(
                                    role.user.get_full_name(), role.project)
                                noti = role.logs.create(source=role.user, type=6, title=description, description=description,
                                 content_type=project, extra_object=self.request.user)
                                result = {}
                                result['description'] = description
                                result['url'] = noti.get_absolute_url()
                                ChannelGroup("notify-{}".format(role.organization.id)).send({"text": json.dumps(result)})
                                ChannelGroup("project-{}".format(role.project.id)).send({"text": json.dumps(result)})
                                ChannelGroup("notify-0").send({"text": json.dumps(result)})

                elif level == "2":
                    for organization_id in data.get('organizations'):
                        organization = Organization.objects.get(pk=organization_id)
                        for user in data.get('users'):
                            role, created = UserRole.objects.get_or_create(user_id=user, organization_id=project_id,
                                                                           group=group)
                            if created:
                                description = "{0} was assigned  as Organization Admin in {1}".format(
                                    role.user.get_full_name(), role.project)
                                noti = role.logs.create(source=role.user, type=7, title=description, description=description,
                                 content_type=organization, extra_object=self.request.user)
                                result = {}
                                result['description'] = description
                                result['url'] = noti.get_absolute_url()
                                ChannelGroup("notify-{}".format(role.organization.id)).send({"text": json.dumps(result)})
                                ChannelGroup("project-{}".format(role.project.id)).send({"text": json.dumps(result)})
                                ChannelGroup("notify-0").send({"text": json.dumps(result)})

        except Exception as e:
            raise ValidationError({
                "User Creation Failed ".format(str(e)),
            })
        return Response({'msg': 'ok'}, status=status.HTTP_200_OK)

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 2

class MultiUserlistViewSet(viewsets.ModelViewSet):
    serializer_class = UserRoleSerializer
    permission_classes = (IsAuthenticated, ManagePeoplePermission)
    # pagination_class = LargeResultsSetPagination
    def get_queryset(self):
        queryset = UserRole.objects.filter(organization__isnull=False, ended_at__isnull=True)
        level = self.kwargs.get('level', None)
        pk = self.kwargs.get('pk', None)
        if level == "0":
            try:
                site = Site.objects.get(pk=pk)
            except Exception as e:
                raise ValidationError({
                    "No such site exists ".format(str(e)),
                })
            queryset = queryset.filter(organization__id=site.project.organization_id).distinct('user_id')
        elif level == "1":
            try:
                project = Project.objects.get(pk=pk)
            except Exception as e:
                raise ValidationError({
                    "No such project exists ".format(str(e)),
                })
            queryset = queryset.filter(organization__id=project.organization_id).distinct('user_id')
        elif level == "2":
            try:
                organization = Organization.objects.get(pk=pk)
            except Exception as e:
                raise ValidationError({
                    "No such organizations exists ".format(str(e)),
                })
            queryset = queryset.filter(organization__id=organization.id).distinct('user_id')
        return queryset

class MultiOPSlistViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, ManagePeoplePermission)
    # pagination_class = LargeResultsSetPagination
    def get_serializer_class(self):
        if self.kwargs.get('level') == "0":
            return SiteSerializer
        elif self.kwargs.get('level') == "1":
            return ProjectTypeSerializer
        else:
            return ProjectTypeSerializer

    def get_queryset(self):
    
        level = self.kwargs.get('level', None)
        pk = self.kwargs.get('pk', None)
        if level == "0":
            queryset = Site.objects.filter(project__id=pk)
        elif level == "1":
            queryset = Project.objects.filter(organization__id=pk)
        return queryset
    