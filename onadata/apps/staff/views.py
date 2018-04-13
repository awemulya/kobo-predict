from django.shortcuts import render, get_object_or_404
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Team, Staff, StaffProject
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from onadata.apps.staff.staffrolemixin import HasStaffRoleMixin, StaffProjectRoleMixin

# Team views:
class TeamList(StaffProjectRoleMixin, ListView):
    model = Team
    template_name = 'staff/team_list.html'

    def get_context_data(self, **kwargs):
        context = super(TeamList, self).get_context_data(**kwargs)
        return context

    def get_queryset(self, queryset):
        queryset = Team.objects.filter(is_deleted=False, staffproject_id=self.kwargs.get('pk'))
        return queryset

class TeamDetail(StaffTeamRoleMixin, DetailView):
    model = Team
    template_name = 'staff/team_detail.html'



class TeamCreate(StaffProjectRoleMixin, CreateView):
    model = Team
    fields = ['leader','name','created_by']
    success_url = reverse_lazy('staff:team-list')


class TeamUpdate(StaffTeamRoleMixin, UpdateView):
    model = Team
    fields = ['leader','name','created_by']
    success_url = reverse_lazy('staff:team-list')


class TeamDelete(StaffProjectRoleMixin, DeleteView):
    model = Team
    success_url = reverse_lazy('staff:team-list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        team_id = self.kwargs['pk']
        team = Team.objects.get(id = team_id)
        team.is_deleted = True
        team.save()
        return HttpResponseRedirect(self.get_success_url())



# Staff views:
class StaffList(StaffTeamRoleMixin, ListView):
    model = Staff
    template_name = 'staff/staff_list.html.html'

    def get_context_data(self, **kwargs):
        context = super(StaffList, self).get_context_data(**kwargs)
        return context

    def get_queryset(self, request, queryset):
        queryset =  Staff.objects.filter(team_id=self.kwargs.get('pk'), is_deleted= False)
        return queryset

class StaffDetail(StaffRoleMixin, DetailView):
    model = Staff
    template_name = 'staff/staff_detail.html'


class StaffCreate(CreateView):
    model = Staff
    fields = ['first_name','last_name', 'gender', 'ethnicity','address','phone_number','bank_name', 'account_number', 'photo', 'designation','created_by']
    success_url = reverse_lazy('staff:staff-list')


class StaffUpdate(StaffRoleMixin, UpdateView):
    model = Staff
    fields = ['first_name','last_name', 'gender', 'ethnicity','address','phone_number','bank_name', 'account_number', 'photo', 'designation','created_by']
    success_url = reverse_lazy('staff:staff-list')


class StaffDelete(DeleteView):
    model = Staff
    success_url = reverse_lazy('staff:staff-list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        staff_id = self.kwargs['pk']
        staff = Staff.objects.get(id = staff_id)
        staff.is_deleted = True
        staff.save()
        return HttpResponseRedirect(self.get_success_url())

#StaffProject Views

class StaffProjectCreate(CreateView):
    model = StaffProject
    fields = ['name','created_by']
    success_url = reverse_lazy('staff:staff-list')

class StaffProjectUpdate(StaffProjectRoleMixin, UpdateView):
    model = StaffProject
    fields = ['name','created_by']
    success_url = reverse_lazy('staff:staff-list')

class StaffProjectList(HasStaffRoleMixin, ListView):
    model = StaffProject
    template_name = 'staff/staffproject_list.html'

    def get_context_data(self, **kwargs):
        context = super(StaffProjectList, self).get_context_data(**kwargs)
        return context

    def get_queryset(self, request, queryset):
        queryset = request.roles.filter(group_id=8, ended_at=None)
        return queryset
