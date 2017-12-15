from __future__ import unicode_literals
import datetime
import json
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import login
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate
from django.views.generic import TemplateView
from rest_framework import parsers
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from onadata.apps.fieldsight.mixins import UpdateView, ProfileView, OwnerMixin, SuperAdminMixin, group_required
from rest_framework import renderers

from channels import Group as ChannelGroup
from onadata.apps.fieldsight.models import Organization
from onadata.apps.userrole.models import UserRole
from onadata.apps.users.models import UserProfile
from onadata.apps.users.serializers import AuthCustomTokenSerializer
from .forms import LoginForm, ProfileForm, UserEditForm
from rest_framework import viewsets
from onadata.apps.fsforms.models import FInstance
from django.db.models import Q

from rest_framework import serializers


class ContactSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    full_name = serializers.ReadOnlyField(source='user.get_full_name')
    role = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'address','gender','phone','skype', 'twitter','tango','hike','qq', 'google_talk',
                  'profile_picture', 'viber', 'whatsapp', 'wechat', 'full_name', 'role', 'primary_number',
                'secondary_number', 'office_number')

    def get_role(self, obj):
        #exclude site supervisors.
        group = Group.objects.get(name__exact="Site Supervisor")
        roles =  UserRole.objects.filter(~Q(group = group),user=obj.user, ended_at__isnull=True)
        role_list =  []
        for r in roles:
            role_list.append({'group':str(r.group), 'project':str(r.project),'site':str(r.site)})
        return role_list


class ContactViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and site Main Stages.
    """
    queryset = UserProfile.objects.filter(organization__isnull=False)
    serializer_class = ContactSerializer

    def filter_queryset(self, queryset):
        project = self.kwargs.get('pk', None)
        if project:
            queryset = queryset.filter(
                user__user_roles__project__id = project,
                user__is_active=True).order_by('user__first_name')
            return queryset
        try:
            org = self.request.user.user_profile.organization
            queryset = queryset.filter(organization = org,user__is_active=True).order_by('user__first_name')
        except:
            queryset = []
        return queryset


def web_authenticate(username=None, password=None):
        try:
            user = User.objects.get(email__iexact=username)
            if user.check_password(password):
                return authenticate(username=user.username, password=password)
        except User.DoesNotExist:
            return None

@api_view(['GET'])
def current_user(request):
    user = request.user
    if user.is_anonymous():
        return Response({'code': 401, 'message': 'Unauthorized User'})
    elif not user.user_profile.organization:
        return Response({'code': 403, 'message': 'Not Assigned to Any Organizations Yet'})
    else:
        site_supervisor = False
        field_sight_info = []
        roles = UserRole.get_active_site_roles(user)
        if roles.exists():
            site_supervisor = True
        for role in roles:
            site = role.site
            data = site.blueprints.all()
            bp = [m.image.url for m in data]
            project = role.project
            site_info = {'site': {'id': site.id, 'phone': site.phone, 'name': site.name, 'description': site.public_desc,
                                  'address':site.address, 'lat': repr(site.latitude), 'lon': repr(site.longitude),
                                  'identifier':site.identifier, 'progress': site.progress(), 'type_id':site.type.id,
                                  'type_label':site.type.name,
                                  'add_desc': site.additional_desc, 'blueprints':bp},
                         'project': {'name': project.name, 'id': project.id, 'description': project.public_desc,
                                     'address':project.address, 'type_id':project.type.id,
                                     'type_label':project.type.name,'phone':project.phone, 'organization_name':project.organization.name,
                                     'organization_url':project.organization.logo.url,
                                     'lat': repr(project.latitude), 'lon': repr(project.longitude)},
                         }
            field_sight_info.append(site_info)

        users_payload = {'username': user.username,
                         'full_name': user.first_name,
                         'email': user.email,
                         'my_sites': field_sight_info,
                         'server_time': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                         'is_supervisor': site_supervisor,
                         'last_login': user.last_login,
                         'organization': user.user_profile.organization.name,
                         'organization_url': user.user_profile.organization.logo.url,
                         'address': user.user_profile.address,
                         'skype': user.user_profile.skype,
                         'phone': user.user_profile.phone,
                         'profile_pic': user.user_profile.profile_picture.url,
                         # 'languages': settings.LANGUAGES,
                         # profile data here, role supervisor
                         }
        response_data = {'code':200, 'data': users_payload}

        return Response(response_data)

# def web_login(request):
#
#     if request.user.is_authenticated():
#         return redirect('/dashboard/')
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             pwd = form.cleaned_data['password']
#             user = web_authenticate(username=email, password=pwd)
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     # request.__class__.organization = role.organization
#                     return HttpResponseRedirect('/fieldsight/')
#                 else:
#                     return render(request, 'registration/login.html', {'form':form, 'inactive':True})
#             else:
#                 return render(request, 'registration/login.html', {'form':form, 'form_errors':True})
#         else:
#             return render(request, 'registration/login.html', {'form': form})
#     else:
#         form = LoginForm()
#
#     return render(request, 'registration/login.html', {'form': form})

# @group_required("admin")


@group_required("admin")
@api_view(['GET'])
def alter_status(request, pk):
    try:
        user = User.objects.get(pk=pk)
        if user.is_active:
            user.is_active = False
            message = "User {0} Deactivated".format(user.get_full_name())
        else:
            user.is_active = True
            message = "User {0} Activated".format(user.get_full_name())
        user.save()
        return Response({'msg': message}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Failure caused by {0}'.format(e.message)}, status=status.HTTP_400_BAD_REQUEST)

def edit(request, pk):
    user = User.objects.get(pk=pk)
    profile, created = UserProfile.objects.get_or_create(user=user)
    if request.method == 'POST':
        form = UserEditForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            address = form.cleaned_data['address']
            gender = form.cleaned_data['gender']
            phone = form.cleaned_data['phone']
            skype = form.cleaned_data['skype']
            user.first_name = name
            user.save()
            profile.address = address
            profile.gender = gender
            profile.phone = phone
            profile.skype = skype
            if not profile.organization:
                organization = form.data.get("organization", False)
                if organization:
                    org = Organization.objects.get(pk=organization)
                    profile.organization = org
            profile.save()

            messages.info(request, 'User Details Updated.')
        return HttpResponseRedirect(reverse('users:users'))

    else:
        form = UserEditForm(initial={'name': user.first_name, 'address':profile.address,'gender':profile.gender,
                                     'phone':profile.phone,'skype':profile.skype})
        organization_list = []
        if not profile.organization:
            organization_list = Organization.objects.all()
        return render(request, 'users/user_form.html', {'form': form, 'id': pk,'name': user.first_name,
                                                        'orglist': organization_list})


def auth_token(request):
    pass


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )

    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        serializer = AuthCustomTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        content = {
            'token': unicode(token.key),
        }

        return Response(content)


class MyProfileView(ProfileView):
    model = UserProfile
    success_url = reverse_lazy('users:profile', kwargs={'pk': 0})
    form_class = ProfileForm


class ProfileUpdateView(MyProfileView, OwnerMixin, UpdateView):
    # pass
    #
    def form_valid(self, form):
        print "sadas333333333"
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        self.object = form.save()
        return HttpResponseRedirect(self.success_url)

        # profile = UserProfile.objects.get(user=user)
    #     profile.address = form.cleaned_data['address']
    #     profile.gender = form.cleaned_data['gender']
    #     profile.phone = form.cleaned_data['phone']
    #     profile.skype = form.cleaned_data['skype']
    #     profile.primary_number = form.cleaned_data['primary_number']
    #     profile.secondary_number = form.cleaned_data['secondary_number']
    #     profile.office_number = form.cleaned_data['office_number']
    #     profile.viber = form.cleaned_data['viber']
    #     profile.whatsapp = form.cleaned_data['whatsapp']
    #     profile.wechat = form.cleaned_data['wechat']
    #     profile.line = form.cleaned_data['line']
    #     profile.tango = form.cleaned_data['tango']
    #     profile.hike = form.cleaned_data['hike']
    #     profile.qq = form.cleaned_data['qq']
    #     profile.google_talk = form.cleaned_data['google_talk']
    #     profile.profile_picture = form.cleaned_data['profile_picture']
    #     profile.save()
    #     # noti = profile.logs.create(source=self.request.user, type=0, title="User",
    #     #                            organization=profile.organization, description="user {0} updated by {1}".
    #     #                            format(user.username, self.request.user.username))
    #     # result = {}
    #     # result['description'] = 'user {0} updated by {1}'.format(user.username, self.request.user.username)
    #     # result['url'] = noti.get_absolute_url()
    #     # ChannelGroup("notify-{}".format(profile.id)).send({"text": json.dumps(result)})
    #     # ChannelGroup("notify-0").send({"text": json.dumps(result)})
    #
    #     return HttpResponseRedirect(self.success_url)


def my_profile(request, pk=None):
    if not pk or pk =='0':
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        # roles = request.user.user_roles.all()
        responses = FInstance.objects.filter(submitted_by = request.user).order_by('-date')[:10]
        return render(request, 'users/profile.html', {'obj': profile, 'roles': "Super Admin", 'responses': responses })
    else:
        user = get_object_or_404(User.objects.filter(pk=pk))
        profile, created = UserProfile.objects.get_or_create(user_id=pk)

        roles_org = user.user_roles.select_related('organization').filter(organization__isnull = False, project__isnull = True, site__isnull = True, ended_at__isnull=True, group__name="Organization Admin")
        roles_project = user.user_roles.select_related('project').filter(organization__isnull = False, project__isnull = False, site__isnull = True, ended_at__isnull=True, group__name="Project Manager")
        roles_reviewer = user.user_roles.select_related('site').filter(organization__isnull = False, project__isnull = False, site__isnull = False, group__name="Reviewer", ended_at__isnull=True)
        roles_SA = user.user_roles.select_related('site').filter(organization__isnull = False, project__isnull = False, site__isnull = False, group__name="Site Supervisor", ended_at__isnull=True)
        responses = FInstance.objects.filter(submitted_by = user).order_by('-date')[:10]
                
        if request.role is not None and request.role.group.name != "Super Admin":
            org_ids = request.user.user_roles.select_related('organization').filter(ended_at__isnull=True).distinct('organization_id').values('organization_id')
            roles_org = roles_org.filter(organization_id__in=org_ids)
            roles_project = roles_project.filter(organization_id__in=org_ids)
            roles_reviewer = roles_reviewer.filter(organization_id__in=org_ids)
            roles_SA = roles_SA.filter(organization_id__in=org_ids)
            responses = FInstance.objects.filter(Q(submitted_by = user) & (Q(site__project__organization_id__in=org_ids) | Q(project__organization_id__in=org_ids))).order_by('-date')[:10]
        return render(request, 'users/profile.html', {'obj': profile, 'roles_org': roles_org, 'roles_project': roles_project, 'roles_site': roles_reviewer, 'roles_SA': roles_SA, 'roles_reviewer': roles_reviewer, 'responses': responses })

class UsersListView(TemplateView, SuperAdminMixin):
    template_name = "users/list.html"


def all_notification(user,  message):
    ChannelGroup("%s" % user).send({
        "text": json.dumps({
            "msg": message
        })
    })