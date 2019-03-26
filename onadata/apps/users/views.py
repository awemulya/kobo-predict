from __future__ import unicode_literals
import datetime
import json
import xlwt, csv

from django.shortcuts import get_object_or_404
from django.core import serializers
from django.contrib import messages
from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import login
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.conf import settings
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate
from django.views.generic import TemplateView, View
from rest_framework import parsers
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.generic import CreateView
from onadata.apps.fieldsight.mixins import UpdateView, ProfileView, OwnerMixin, SuperAdminMixin, group_required
from rest_framework import renderers
from django.contrib import messages
from channels import Group as ChannelGroup
from onadata.apps.fieldsight.models import Organization, BluePrints, UserInvite, Site, Project, RequestOrganizationStatus, Region
from onadata.apps.userrole.models import UserRole
from onadata.apps.users.models import UserProfile
from onadata.apps.users.serializers import AuthCustomTokenSerializer, UserSerializerProfile

from .forms import LoginForm, ProfileForm, UserEditForm, SignUpForm
from rest_framework import viewsets
from onadata.apps.fsforms.models import FInstance
from django.db.models import Q
from onadata.apps.fieldsight.rolemixins import LoginRequiredMixin, EndRoleMixin
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .signup_tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import password_reset



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
            role_list.append({'group':u'{}'.format(r.group), 'project':u'{}'.format(r.project),'site':u'{}'.format(r.site)})
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


# def web_authenticate(username=None, password=None):
#         # returns User , Email_correct, Password_correct
#         try:
#             user = User.objects.get(email__iexact=username)
#             if user.check_password(password):
#                 return authenticate(username=user.username, password=password)
#             else:
#                 return None, True, False
#         except User.DoesNotExist:
#             return None, False, True

@api_view(['GET'])
def current_user(request):
    user = request.user
    if user.is_anonymous():
        return Response({'code': 401, 'message': 'Unauthorized User'})
    elif not user.user_profile.organization:
        return Response({'code': 403, 'message': 'Sorry, you are not assigned to any organization yet. '
                                                 'Please contact your project manager.'})
    else:
        site_supervisor = False
        field_sight_info = []
        count = UserRole.get_active_site_roles_count(user)
        if count == 0:
            return Response({'code': 403, 'message': 'Sorry, you are not assigned to any Sites yet. '
                                                     'Please contact your project manager.'})
        if count >= 500:
            return Response({'code': 403, 'message': 'Sorry, you are assigned Many Sites. > 500 '
                                                     'Please contact your project manager.'})
        roles = UserRole.get_active_site_roles(user)
        blue_prints = []
        if roles.exists():
            site_supervisor = True
            blue_prints = BluePrints.objects.filter(site__project__organization=user.user_profile.organization)
        for role in roles:
            site = role.site
            site_type = 0
            site_type_level = ""
            try:
                site_type = site.type.id
                site_type_level = site.type.name
            except Exception as e:
                pass
            bp = [m.image.url for m in blue_prints if m.site == site]
            project = role.project
            site_info = {'site': {'id': site.id, 'phone': site.phone, 'name': site.name, 'description': site.public_desc,
                                  'address':site.address, 'lat': repr(site.latitude), 'lon': repr(site.longitude),
                                  'identifier':site.identifier, 'progress': 0, 'type_id':site_type,
                                  'type_label':site_type_level,
                                  'add_desc': site.additional_desc, 'blueprints':bp, 'site_meta_attributes_ans':site.site_meta_attributes_ans},
                         'project': {'name': project.name, 'id': project.id, 'description': project.public_desc,
                                     'address':project.address, 'type_id':project.type.id,
                                     'type_label':project.type.name,'phone':project.phone, 'organization_name':project.organization.name,
                                     'organization_url':project.organization.logo.url,
                                     'lat': repr(project.latitude), 'lon': repr(project.longitude), 'cluster_sites':project.cluster_sites, 'site_meta_attributes':project.site_meta_attributes},
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

@api_view(['GET'])
def current_usertwo(request):
    user = request.user
    if user.is_anonymous():
        return Response({'code': 401, 'message': 'Unauthorized User'})
    elif not user.user_profile.organization:
        return Response({'code': 403, 'message': 'Sorry, you are not assigned to any organization yet. '
                                                 'Please contact your project manager.'})
    else:
        site_supervisor = UserRole.get_active_site_roles_exists(user)
        users_payload = {'username': user.username,
                         'full_name': user.first_name,
                         'email': user.email,
                         'server_time': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                         'is_supervisor': site_supervisor,
                         'last_login': user.last_login,
                         'organization': user.user_profile.organization.name,
                         'organization_url': user.user_profile.organization.logo.url,
                         'address': user.user_profile.address,
                         'skype': user.user_profile.skype,
                         'phone': user.user_profile.phone,
                         'profile_pic': user.user_profile.profile_picture.url,
                         'profile_data':UserSerializerProfile(user.user_profile).data
                         # 'languages': settings.LANGUAGES,
                         # profile data here, role supervisor
                         }
        response_data = {'code':200, 'data': users_payload}

        return Response(response_data)


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


class ProfileCreateView(MyProfileView, CreateView):
    def form_valid(self, form):
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        form.instance.user = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(reverse_lazy('users:view_invitations', kwargs={'pk':user.pk}))


class ProfileUpdateView(MyProfileView, OwnerMixin, UpdateView):
    # pass
    #
    def form_valid(self, form):
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        self.object = form.save()
        return HttpResponseRedirect(reverse_lazy('users:profile', kwargs={'pk': self.object.user.pk}))


class MyProfile(LoginRequiredMixin, View):

    def get(self, request, pk=None):
        if not pk or pk =='0':
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            # roles = request.user.user_roles.all()
            responses = FInstance.objects.filter(submitted_by = request.user).order_by('-date')[:10]
            return render(request, 'users/profile.html', {'obj': profile, 'responses': responses })
            # return render(request, 'users/profile.html', {'obj': profile, 'roles': "Super Admin", 'responses': responses })
        else:
            user = get_object_or_404(User.objects.filter(pk=pk))
            profile, created = UserProfile.objects.get_or_create(user_id=pk)

            roles_org = user.user_roles.select_related('organization').filter(organization__isnull = False, project__isnull = True, site__isnull = True, ended_at__isnull=True, group__name="Organization Admin")
            roles_project = user.user_roles.select_related('project').filter(organization__isnull = False, project__isnull = False, site__isnull = True, ended_at__isnull=True, group__name="Project Manager")
            roles_reviewer = user.user_roles.select_related('site').filter(organization__isnull = False, project__isnull = False, site__isnull = False, group__name="Reviewer", ended_at__isnull=True)
            roles_SA = user.user_roles.select_related('site').filter(organization__isnull = False, project__isnull = False, site__isnull = False, group__name="Site Supervisor", ended_at__isnull=True)
            roles_region_supervisor = user.user_roles.select_related('region').filter(organization__isnull=False, project__isnull=False, region__isnull=False, group__name="Region Supervisor", ended_at__isnull=True)
            roles_region_reviewer = user.user_roles.select_related('region').filter(organization__isnull=False, project__isnull=False, region__isnull=False, group__name="Region Reviewer", ended_at__isnull=True)

            responses = FInstance.objects.filter(submitted_by = user).order_by('-date')[:10]
            
            if request.role is not None and request.role.group.name != "Super Admin":
                org_ids = request.user.user_roles.select_related('organization').filter(ended_at__isnull=True).distinct('organization_id').values('organization_id')
                roles_org = roles_org.filter(organization_id__in=org_ids)
                roles_project = roles_project.filter(organization_id__in=org_ids)
                roles_reviewer = roles_reviewer.filter(organization_id__in=org_ids)
                roles_SA = roles_SA.filter(organization_id__in=org_ids)
                responses = FInstance.objects.filter(Q(submitted_by = user) & (Q(site__project__organization_id__in=org_ids) | Q(project__organization_id__in=org_ids))).order_by('-date')[:10]
            
                own_manager_roles=request.user.user_roles.filter(group_id=2, ended_at__isnull=True).values_list('project_id', flat=True)
                own_org_admin=request.user.user_roles.filter(group_id=1, ended_at__isnull=True).values_list('organization_id', flat=True)
                is_super_admin = False
            else:
                own_manager_roles =[]
                own_org_admin=[]
                
                if request.role.group.name == "Super Admin":
                    is_super_admin = True
                else:
                    is_super_admin = False
            return render(request, 'users/profile.html', {'obj': profile, 'is_super_admin': is_super_admin,
                                                          'own_orgs': own_org_admin, 'own_projects': own_manager_roles,
                                                          'roles_org': roles_org, 'roles_project': roles_project,
                                                          'roles_site': roles_reviewer, 'roles_SA': roles_SA,
                                                          'roles_reviewer': roles_reviewer, 'responses': responses,
                                                          'roles_region_reviewer': roles_region_reviewer,
                                                          'roles_region_supervisor': roles_region_supervisor
                                                          })


class EndUserRole(EndRoleMixin, View):

    def get(self, request, pk):
        userrole=UserRole.objects.get(pk=pk)
        userrole.ended_at = datetime.datetime.now()
        userrole.save()
        next_url = request.GET.get('next', '/')
        # return None
        messages.success(request, 'Role Sucessfully Unassigned.')
        return HttpResponseRedirect(next_url)


class UsersListView(TemplateView, SuperAdminMixin):
    template_name = "users/list.html"


class ViewInvitations(LoginRequiredMixin, TemplateView):
    template_name = "users/invitations.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            user = User.objects.get(pk=kwargs.get('pk'))

            if request.user == user:
                return super(ViewInvitations, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()

    def get_context_data(self, *args, **kwargs):
        context = super(ViewInvitations, self).get_context_data(*args, **kwargs)

        email = User.objects.values('email').get(pk=kwargs.get('pk'))
        context['has_org'] = Organization.objects.filter(owner=self.request.user).exists()
        context['invitations'] = UserInvite.objects.filter(email=email['email'], is_used=False, is_declied=False)
        return context


def all_notification(user, message):
    ChannelGroup("%s" % user).send({
        "text": json.dumps({
            "msg": message
        })
    })

def web_authenticate(username=None, password=None):
        try:
            if "@" in username:
                user = User.objects.get(email__iexact=username)
            else:
                user = User.objects.get(username__iexact=username)
            if user.check_password(password):
                return authenticate(username=user.username, password=password), False
            else:
                return None, True  # Email is correct
        except User.DoesNotExist:
            return None, False   # false Email incorrect


def web_login(request):
    reset = request.GET.get('reset')
    if request.user.is_authenticated():
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            pwd = form.cleaned_data['password']
            user, valid_email = web_authenticate(username=username, password=pwd)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('dashboard'))
                else:
                    return render(request, 'users/login.html',
                                  {'form': form,
                                   'email_error': "Your Account is Deactivated, Please Contact Administrator.",
                                   'valid_email': valid_email,
                                   'login_username':username
                                   })
            else:
                if valid_email:
                    email_error = False
                    password_error = True
                else:
                    password_error = False
                    email_error = "Invalid Email, Please Check your Email Address."
                return render(request, 'users/login.html',
                              {'form': form,
                               'valid_email': valid_email,
                               'email_error': email_error,
                               'password_error': password_error,
                               'login_username':username
                               })
        else:
            if request.POST.get('login_username') != None:
                login_username = request.POST.get('login_username')
            else:
                login_username = ''
            return render(request, 'users/login.html', {
                'form': form ,
                'valid_email': False,
                'email_error': "Your Email and Password Didnot Match.",
                'login_username':login_username,
                })
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form,
    'valid_email': True,
    'email_error': False,
    'reset':reset
    })


def web_signup(request):
    if request.user.is_authenticated():
        return redirect('/')
    if request.method == 'POST':
        signup_form = SignUpForm(request.POST)
        if signup_form.is_valid():
            username = signup_form.cleaned_data.get('username')
            email = signup_form.cleaned_data.get('email')
            password = signup_form.cleaned_data.get('password')
            user = User.objects.create(username=username, email=email, password=password)
            user.set_password(user.password)
            user.is_active = False
            user.save()

            codenames = ['add_asset', 'change_asset', 'delete_asset', 'view_asset', 'share_asset', 'add_finstance',
                         'change_finstance', 'add_instance', 'change_instance']
            permissions = Permission.objects.filter(codename__in=codenames)
            for permission in permissions:
                user.user_permissions.add(permission)

            group = Group.objects.get(name="Unassigned")
            UserRole.objects.create(user=user, group=group)

            mail_subject = 'Activate your account.'
            current_site = get_current_site(request)
            message = render_to_string('users/acc_active_email.html', {
                'user': user,
                'domain': settings.SITE_URL,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = email
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'users/login.html', {
                'signup_form':signup_form,
                'valid_email':True,
                'email_error':False,
                'success_signup':1,
                'email':to_email,
                })

            # user = authenticate(username=username,
            #                         password=password,
            #                         )
            # login(request, user)
            #
            # return HttpResponseRedirect('/fieldsight/myroles/')

        else:
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            return render(request, 'users/login.html', {
                'signup_form':signup_form,
                'username':username,
                'email':email,
                'valid_email': True,
                'email_error':False,
                'signup_tab': 1,
                'success_signup':0,
                })
    else:
        signup_form = SignUpForm()
        return render(request, 'users/login.html', {'signup_form':signup_form,
        'valid_email':True,
        'email_error': False,
        'success_signup':0})


def create_role(request):
    user = User.objects.latest('date_joined')
    group = Group.objects.get(name="Unassigned")
    try:
        UserRole.objects.get(user=user)
    except UserRole.DoesNotExist:
        UserRole.objects.create(user=user, group=group)

    return HttpResponseRedirect('/fieldsight/myroles/')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        return redirect(reverse_lazy('users:create_profile'))
    else:
        return HttpResponse('Activation link is invalid!')


def decline_invitation(request, pk, username):
    user = get_object_or_404(User, username=username)
    invitation = get_object_or_404(UserInvite, pk=pk)
    invitation.is_used = True
    invitation.is_declined = True
    invitation.save()

    return redirect(reverse_lazy('users:view_invitations', kwargs={'pk': user.pk}))


@transaction.atomic
def accept_invitation(request, pk, username):
    user = get_object_or_404(User, username=username)
    invitation = get_object_or_404(UserInvite, pk=pk)

    if user.user_roles.all()[0].group.name == "Unassigned":
        previous_group = UserRole.objects.get(user=user, group__name="Unassigned")
        previous_group.delete()

    site_ids = invitation.site.all().values_list('pk', flat=True)
    project_ids = invitation.project.all().values_list('pk', flat=True)

    if invitation.regions.all().values_list('pk', flat=True).exists():
        regions_id = invitation.regions.all().values_list('pk', flat=True)
        for region_id in regions_id:
            project_id = Region.objects.get(id=region_id).project.id
            userrole, created = UserRole.objects.get_or_create(user=user, group=invitation.group,
                                                               organization=invitation.organization,
                                                               project_id=project_id,
                                                               site_id=None, region_id=region_id)

    else:
        for project_id in project_ids:
            for site_id in site_ids:
                userrole, created = UserRole.objects.get_or_create(user=user, group=invitation.group,
                                                                   organization=invitation.organization,
                                                                   project_id=project_id, site_id=site_id)
            if not site_ids:
                userrole, created = UserRole.objects.get_or_create(user=user, group=invitation.group,
                                                                   organization=invitation.organization,
                                                                   project_id=project_id, site=None)

    if not project_ids:
        userrole, created = UserRole.objects.get_or_create(user=user, group=invitation.group,
                                                           organization=invitation.organization, project=None,
                                                           site=None, region=None)
        if invitation.group_id == 1:
            permission = Permission.objects.filter(codename='change_finstance')
            user.user_permissions.add(permission[0])

    invitation.is_used = True
    invitation.save()
    extra_msg = ""
    site = None
    project = None
    region = None
    if invitation.group.name == "Organization Admin":
        noti_type = 1
        content = invitation.organization

    elif invitation.group.name == "Project Manager":
        if invitation.project.all().count() == 1:
            noti_type = 2
            content = invitation.project.all()[0]
        else:
            noti_type = 26
            extra_msg = invitation.project.all().count()
            content = invitation.organization
        project = invitation.project.all()[0]

    elif invitation.group.name == "Reviewer":
        if invitation.site.all().count() == 1:
            noti_type = 3
            content = invitation.site.all()[0]
        else:
            noti_type = 27
            extra_msg = invitation.site.all().count()
            content = invitation.project.all()[0]
        project = invitation.project.all()[0]

    elif invitation.group.name == "Site Supervisor":
        if invitation.site.all().count() == 1:
            noti_type = 4
            content = invitation.site.all()[0]
        else:
            noti_type = 28
            extra_msg = invitation.site.all().count()
            content = invitation.project.all()[0]
        project = invitation.project.all()[0]

    elif invitation.group.name == "Region Reviewer":
        if invitation.regions.all().count() == 1:
            noti_type = 37
            content = invitation.regions.all()[0]
        else:
            noti_type = 39
            extra_msg = invitation.regions.all().count()
            content = invitation.project.all()[0]
        project = invitation.project.all()[0]

    elif invitation.group.name == "Region Supervisor":
        if invitation.regions.all().count() == 1:
            noti_type = 38
            content = invitation.regions.all()[0]
        else:
            noti_type = 40
            extra_msg = invitation.regions.all().count()
            content = invitation.project.all()[0]
        project = invitation.project.all()[0]

    elif invitation.group.name == "Unassigned":
        noti_type = 24
        # if invitation.site.all():
        #     content = invitation.site.all()[0]
        #     project = invitation.project.all()[0]
        #     site = invitation,project.all()[0]
        # elif invitation.project.all().count():
        #     content = invitation.project.all()[0]
        #     project = invitation.project.all()[0]
        # else:
        content = invitation.organization

    elif invitation.group.name == "Project Donor":
        noti_type = 25
        content = invitation.project.all()[0]

    noti = invitation.logs.create(source=user, type=noti_type, title="new Role",
                                  organization=invitation.organization,
                                  extra_message=extra_msg, project=project, site=site, content_object=content,
                                  extra_object=invitation.by_user,
                                  description="{0} was added as the {1} of {2} by {3}.".
                                  format(user.username, invitation.group.name, content.name, invitation.by_user))


    return redirect(reverse_lazy('users:view_invitations', kwargs={'pk': user.pk}))


@transaction.atomic
def accept_all_invitations(request, username):
    user = get_object_or_404(User, username=username)
    invitations = UserInvite.objects.filter(email=user.email, is_used=False, is_declied=False)


    if user.user_roles.all()[0].group.name == "Unassigned":
        previous_group = UserRole.objects.get(user=user, group__name="Unassigned")
        previous_group.delete()

    for invitation in invitations:
        site_ids = invitation.site.all().values_list('pk', flat=True)
        project_ids = invitation.project.all().values_list('pk', flat=True)
        if invitation.regions.all().values_list('pk', flat=True).exists():
            regions_id = invitation.regions.all().values_list('pk', flat=True)
            for region_id in regions_id:
                project_id = Region.objects.get(id=region_id).project.id
                userrole, created = UserRole.objects.get_or_create(user=user, group=invitation.group,
                                                                   organization=invitation.organization,
                                                                   project_id=project_id,
                                                                   site_id=None, region_id=region_id)

        else:
            for project_id in project_ids:
                for site_id in site_ids:
                    userrole, created = UserRole.objects.get_or_create(user=user, group=invitation.group,
                                                                       organization=invitation.organization,
                                                                       project_id=project_id, site_id=site_id)
                if not site_ids:
                    userrole, created = UserRole.objects.get_or_create(user=user, group=invitation.group,
                                                                       organization=invitation.organization,
                                                                       project_id=project_id, site=None)

        if not project_ids:
            userrole, created = UserRole.objects.get_or_create(user=user, group=invitation.group,
                                                               organization=invitation.organization, project=None,
                                                               site=None, region=None)
            if invitation.group_id == 1:
                permission = Permission.objects.filter(codename='change_finstance')
                user.user_permissions.add(permission[0])

        invitation.is_used = True
        invitation.save()
        extra_msg = ""
        site = None
        project = None
        region = None
        if invitation.group.name == "Organization Admin":
            noti_type = 1
            content = invitation.organization

        elif invitation.group.name == "Project Manager":
            if invitation.project.all().count() == 1:
                noti_type = 2
                content = invitation.project.all()[0]
            else:
                noti_type = 26
                extra_msg = invitation.project.all().count()
                content = invitation.organization
            project = invitation.project.all()[0]

        elif invitation.group.name == "Reviewer":
            if invitation.site.all().count() == 1:
                noti_type = 3
                content = invitation.site.all()[0]
            else:
                noti_type = 27
                extra_msg = invitation.site.all().count()
                content = invitation.project.all()[0]
            project = invitation.project.all()[0]

        elif invitation.group.name == "Site Supervisor":
            if invitation.site.all().count() == 1:
                noti_type = 4
                content = invitation.site.all()[0]
            else:
                noti_type = 28
                extra_msg = invitation.site.all().count()
                content = invitation.project.all()[0]
            project = invitation.project.all()[0]

        elif invitation.group.name == "Region Reviewer":
            if invitation.regions.all().count() == 1:
                noti_type = 37
                content = invitation.regions.all()[0]
            else:
                noti_type = 39
                extra_msg = invitation.regions.all().count()
                content = invitation.project.all()[0]
            project = invitation.project.all()[0]

        elif invitation.group.name == "Region Supervisor":
            if invitation.regions.all().count() == 1:
                noti_type = 38
                content = invitation.regions.all()[0]
            else:
                noti_type = 40
                extra_msg = invitation.regions.all().count()
                content = invitation.project.all()[0]
            project = invitation.project.all()[0]

        elif invitation.group.name == "Unassigned":
            noti_type = 24
            # if invitation.site.all():
            #     content = invitation.site.all()[0]
            #     project = invitation.project.all()[0]
            #     site = invitation,project.all()[0]
            # elif invitation.project.all().count():
            #     content = invitation.project.all()[0]
            #     project = invitation.project.all()[0]
            # else:
            content = invitation.organization

        elif invitation.group.name == "Project Donor":
            noti_type = 25
            content = invitation.project.all()[0]

        noti = invitation.logs.create(source=user, type=noti_type, title="new Role",
                                      organization=invitation.organization,
                                      extra_message=extra_msg, project=project, site=site, content_object=content,
                                      extra_object=invitation.by_user,
                                      description="{0} was added as the {1} of {2} by {3}.".
                                      format(user.username, invitation.group.name, content.name, invitation.by_user))

    return redirect(reverse_lazy('users:view_invitations', kwargs={'pk': user.pk}))


def export_users_xls(request):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="FieldsightUsers.csv"'

    writer = csv.writer(response)

    writer.writerow(['First Name', 'Last Name', 'Username', 'Email', 'Organization'])
    users = User.objects.all()
    for u in users:
        org = u.user_roles.all().values('organization__name').distinct()
        org_list = []
        for i in org:
            org_list.append(i['organization__name'])

        writer.writerow([u.first_name, u.last_name, u.username, u.email, org_list])

    return response