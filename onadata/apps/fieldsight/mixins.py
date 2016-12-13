from functools import wraps

from django.http import JsonResponse
from django.views.generic.edit import UpdateView as BaseUpdateView, CreateView as BaseCreateView, DeleteView as BaseDeleteView
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from .helpers import json_from_object


class DeleteView(BaseDeleteView):
    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = super(DeleteView, self).post(request, *args, **kwargs)
        messages.success(request, ('%s %s' % (self.object.__class__._meta.verbose_name.title(), _('successfully deleted!'))))
        return response


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwargs):
        view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        return login_required(view)


class OrganizationRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.organization:
            raise PermissionDenied()
        if hasattr(self, 'check'):
            if not getattr(request.organization, self.check)():
                raise PermissionDenied()
        return super(OrganizationRequiredMixin, self).dispatch(request, *args, **kwargs)


class ProjectRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.project:
            raise PermissionDenied()
        if hasattr(self, 'check'):
            if not getattr(request.project, self.check)():
                raise PermissionDenied()
        return super(ProjectRequiredMixin, self).dispatch(request, *args, **kwargs)


class SiteRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.site:
            raise PermissionDenied()
        if hasattr(self, 'check'):
            if not getattr(request.project, self.check)():
                raise PermissionDenied()
        return super(SiteRequiredMixin, self).dispatch(request, *args, **kwargs)


class UpdateView(BaseUpdateView):
    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['scenario'] = _('Edit')
        context['base_template'] = 'base.html'
        super(UpdateView, self).get_context_data()
        return context


class CreateView(BaseCreateView):
    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['scenario'] = _('Add')
        if self.request.is_ajax():
            base_template = '_modal.html'
        else:
            base_template = 'base.html'
        context['base_template'] = base_template
        return context


class AjaxableResponseMixin(object):
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            if 'ret' in self.request.GET:
                obj = getattr(self.object, self.request.GET['ret'])
            else:
                obj = self.object
            return json_from_object(obj)
        else:
            return response


class TableObjectMixin(TemplateView):
    def get_context_data(self, *args, **kwargs):
        context = super(TableObjectMixin, self).get_context_data(**kwargs)
        if self.kwargs:
            pk = int(self.kwargs.get('pk'))
            obj = get_object_or_404(self.model, pk=pk, company=self.request.company)
            scenario = 'Update'
        else:
            obj = self.model(company=self.request.company)
            # if obj.__class__.__name__ == 'PurchaseVoucher':
            #     tax = self.request.company.settings.purchase_default_tax_application_type
            #     tax_scheme = self.request.company.settings.purchase_default_tax_scheme
            #     if tax:
            #         obj.tax = tax
            #     if tax_scheme:
            #         obj.tax_scheme = tax_scheme
            scenario = 'Create'
        data = self.serializer_class(obj).data
        context['data'] = data
        context['scenario'] = scenario
        context['obj'] = obj
        return context


class TableObject(object):
    def get_context_data(self, *args, **kwargs):
        context = super(TableObject, self).get_context_data(**kwargs)
        if self.kwargs:
            pk = int(self.kwargs.get('pk'))
            obj = get_object_or_404(self.model, pk=pk, company=self.request.company)
            scenario = 'Update'
        else:
            obj = self.model(company=self.request.company)
            # if obj.__class__.__name__ == 'PurchaseVoucher':
            #     tax = self.request.company.settings.purchase_default_tax_application_type
            #     tax_scheme = self.request.company.settings.purchase_default_tax_scheme
            #     if tax:
            #         obj.tax = tax
            #     if tax_scheme:
            #         obj.tax_scheme = tax_scheme
            scenario = 'Create'
        data = self.serializer_class(obj).data
        context['data'] = data
        context['scenario'] = scenario
        context['obj'] = obj
        return context


class OrganizationView(LoginRequiredMixin):
    def form_valid(self, form):
        if self.request.organization:
            form.instance.organization = self.request.organization
        return super(OrganizationView, self).form_valid(form)

    def get_queryset(self):
        if self.request.organization:
            return super(OrganizationView, self).get_queryset().filter(organization=self.request.organization)
        else:
            return super(OrganizationView, self).get_queryset()

    def get_form(self, *args, **kwargs):
        form = super(OrganizationView, self).get_form(*args, **kwargs)
        if self.request.organization:
            form.organization = self.request.organization
        if hasattr(form.Meta, 'organization_filters'):
            for field in form.Meta.organization_filters:
                form.fields[field].queryset = form.fields[field].queryset.filter(organization=form.organization)
        return form


class ProjectView(ProjectRequiredMixin):
    def form_valid(self, form):
        form.instance.project = self.request.project
        return super(ProjectView, self).form_valid(form)

    def get_queryset(self):
        return super(ProjectView, self).get_queryset().filter(project=self.request.project)

    def get_form(self, *args, **kwargs):
        form = super(ProjectView, self).get_form(*args, **kwargs)
        form.project = self.request.project
        if hasattr(form.Meta, 'project_filters'):
            for field in form.Meta.project_filters:
                form.fields[field].queryset = form.fields[field].queryset.filter(project=form.project)
        return form


class SiteView(SiteRequiredMixin):
    def form_valid(self, form):
        form.instance.site = self.request.site
        return super(SiteView, self).form_valid(form)

    def get_queryset(self):
        return super(SiteView, self).get_queryset().filter(site=self.request.site)

    def get_form(self, *args, **kwargs):
        form = super(SiteView, self).get_form(*args, **kwargs)
        form.site = self.request.site
        if hasattr(form.Meta, 'site_filters'):
            for field in form.Meta.site_filters:
                form.fields[field].queryset = form.fields[field].queryset.filter(site=form.site)
        return form



USURPERS = {
    # central engineer to project , same on roles.
    'Site': ['Central Engineer', 'Site Supervisor', 'Data Entry'],
    'KoboForms': ['Project Manager', 'Central Engineer'],
    'Project': ['Project Manager'],
    'Organization': ['Organization Admin', 'Super Admin'],
    'admin': ['Super Admin'],
}


class SiteMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.role.group.name in USURPERS['Site']:
                return super(SiteMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()


class ProjectMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.role.group.name in USURPERS['Project']:
                return super(ProjectMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()


class KoboFormsMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.role.group.name in USURPERS['KoboForms']:
                return super(KoboFormsMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()


#use in view class
class OrganizationMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.role.group.name in USURPERS['Organization']:
                return super(OrganizationMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()


class SuperAdminMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.role.group.name in USURPERS['admin']:
                return super(SuperAdminMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()


# use in all view functions
def group_required(group_name):
    def _check_group(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated():
                if request.role.group.name in USURPERS.get(group_name, []):
                    return view_func(request, *args, **kwargs)
            raise PermissionDenied()

        return wrapper

    return _check_group


