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

from onadata.apps.userrole.models import UserRole
from onadata.apps.users.models import UserProfile
from onadata.apps.users.serializers import AuthCustomTokenSerializer
from .forms import LoginForm, ProfileForm


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
    else:
        site_supervisor = False
        field_sight_info = []
        roles = UserRole.get_active_site_roles(user)
        if roles.exists():
            site_supervisor =True
        for role in roles:
            site = role.site
            project = site.project
            organization = project.organization
            # central_engineers = [ob.as_json() for ob in UserRole.central_engineers(site)]
            # project_managers = [ob.as_json() for ob in UserRole.project_managers(project)]
            # organization_admins = [ob.as_json() for ob in UserRole.organization_admins(organization)]
            site_info = {'site': {'id': site.id, 'name': site.name},
                         'project': {'name': project.name, 'id': project.id},
                         'organization': {'name': organization.name, 'id':organization.id}}
            field_sight_info.append(site_info)

        users_payload = {'username': user.username,
                         'full_name': user.first_name,
                         'email': user.email,
                         'my_sites': field_sight_info,
                         'server_time': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                         'is_supervisor': site_supervisor,
                         'last_login': user.last_login,
                         # 'languages': settings.LANGUAGES,
                         # profile data here, role supervisor
                         }
        response_data = {'code':200, 'data': users_payload}

        return Response(response_data)

def web_login(request):
    if request.user.is_authenticated():
        return redirect('/dashboard/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            pwd = form.cleaned_data['password']
            user = web_authenticate(username=email, password=pwd)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/fieldsight/')
                else:
                    return render(request, 'registration/login.html', {'form':form, 'inactive':True})
            else:
                return render(request, 'registration/login.html', {'form':form, 'form_errors':True})
        else:
            return render(request, 'registration/login.html', {'form': form})
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})

# @group_required("admin")


def alter_status(request, pk):
    try:
        user = User.objects.get(pk=int(pk))
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
    obj = UserProfile.objects.get(user=request.user)
    return render(request, 'users/profile.html', {'obj':obj})

