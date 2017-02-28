from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import ListView

from onadata.apps.fieldsight.mixins import (LoginRequiredMixin, SuperAdminMixin, CreateView, UpdateView, DeleteView,
                                            AjaxableResponseMixinUser)
from .forms import UserRoleForm, UserForm
from .models import UserRole as Role, UserRole


def set_role(request, pk):
    role = Role.objects.get(pk=pk, user=request.user)
    if role:
        request.session['role'] = role.pk
    return redirect(request.META.get('HTTP_REFERER', '/'))


class UserRoleView(object):
    model = UserRole
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



