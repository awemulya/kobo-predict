import datetime

from django.core import serializers
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate
from rest_framework import parsers
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from onadata.apps.fieldsight.mixins import UpdateView, ProfileView
from rest_framework import renderers

from onadata.apps.fieldsight.models import Organization
from onadata.apps.userrole.models import UserRole
from onadata.apps.users.models import UserProfile
from onadata.apps.users.serializers import AuthCustomTokenSerializer
from .forms import LoginForm, ProfileForm, UserEditForm


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
            project = site.project
            site_info = {'site': {'id': site.id, 'name': site.name, 'description': site.public_desc,
                                  'lat': site.latitude, 'lon':site.longitude},
                         'project': {'name': project.name, 'id': project.id,
                                     'description': project.public_desc, 'lat':project.latitude, 'lon':project.longitude},
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


def alter_status(request, pk):
    try:
        user = User.objects.get(pk=pk)
            # alter status method on custom user
        if user.is_active:
            user.is_active = False
            messages.info(request, 'User {0} Deactivated.'.format(user.get_full_name()))
        else:
            user.is_active = True
            messages.info(request, 'User {0} Activated.'.format(user.get_full_name()))
        user.save()
    except:
        messages.info(request, 'User {0} not found.'.format(user.get_full_name()))
    return HttpResponseRedirect(reverse('fieldsight:user-list'))


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
        return HttpResponseRedirect(reverse('fieldsight:user-list'))

    else:
        form = UserEditForm(initial={'name': user.first_name, 'address':profile.address,'gender':profile.gender,
                                     'phone':profile.phone,'skype':profile.skype})
        organization_list = []
        if not profile.organization:
            organization_list = Organization.objects.filter(is_active=True)
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
    success_url = reverse_lazy('users:profile')
    form_class = ProfileForm


class ProfileUpdateView(MyProfileView, UpdateView):
    pass


def my_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'users/profile.html', {'obj':profile})

