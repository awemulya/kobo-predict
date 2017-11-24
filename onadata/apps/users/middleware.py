from onadata.apps.userrole.models import UserRole as Role
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout

from django.shortcuts import get_object_or_404, render, redirect



def clear_roles(request):
    request.__class__.role = None
    request.__class__.organization = None
    request.__class__.project = None
    request.__class__.site = None
    request.__class__.group = None
    request.__class__.roles = []
    request.__class__.is_super_admin = False
    # request.__class__.groups = []
    return request


class RoleMiddleware(object):
    def process_request(self, request):

        if request.META.get('HTTP_AUTHORIZATION'):
            token_key = request.META.get('HTTP_AUTHORIZATION').split(' ')[-1]
            try:
                request.user = Token.objects.get(key=token_key).user
            except:
                pass

        if not request.user.is_anonymous():

            role = None
            if request.session.get('role'):
                try:
                    role = Role.objects.select_related('group', 'organization').get(pk=request.session.get('role'),
                                                                                    user=request.user)
                except Role.DoesNotExist:
                    pass

            if not role:
                roles = Role.get_active_roles(request.user)
                # roles = Role.objects.filter(user=request.user).select_related('group', 'organization')
                if roles:
                    role = roles[0]
                    request.session['role'] = role.id
            if role:
                request.__class__.role = role
                request.__class__.organization = role.organization
                request.__class__.project = role.project
                request.__class__.site = role.site
                request.__class__.group = role.group
                # request.__class__.roles = Role.objects.filter(user=request.user, organization=role.organization)
                request.__class__.roles = Role.get_active_roles(request.user)
                request.__class__.is_super_admin = request.group.name in ('Super Admin')
                #     for role in request.roles:
                #         groups.append(role.group)
                #     request.__class__.groups = groups
            else:
                # request = clear_roles(request)
                logout(request)

                return render(request, 'fieldsight/permission_denied.html')

        else:
            request = clear_roles(request)

    def authenticate(self, request):
        pass

