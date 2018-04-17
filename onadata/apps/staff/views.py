from django.shortcuts import render, get_object_or_404
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Team, Staff, StaffProject
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from onadata.apps.staff.staffrolemixin import HasStaffRoleMixin, StaffProjectRoleMixin, StaffTeamRoleMixin, StaffRoleMixin
from django.contrib.auth.models import User
from onadata.apps.staff.forms import TeamForm, StaffForm
# Team views:

class TeamList(StaffProjectRoleMixin, ListView):
    model = Team
    template_name = 'staff/team_list.html'

    def get_context_data(self, **kwargs):
        context = super(TeamList, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context

    def get_queryset(self):
        queryset = Team.objects.filter(is_deleted=False, staffproject_id=self.kwargs.get('pk'))
        return queryset

class TeamDelete(StaffProjectRoleMixin, DeleteView):
    model = Team

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        team_id = self.kwargs['pk']
        team = Team.objects.get(id = team_id)
        team.is_deleted = True
        team.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('staff:staff-project-detail', kwargs={'pk': self.object.staffproject_id})



class TeamCreate(StaffProjectRoleMixin, CreateView):
    form_class = TeamForm
    model = Team
    def form_valid(self, form):
        form.instance.staffproject_id = self.kwargs.get('pk')
        form.instance.created_by = self.request.user
        return super(TeamCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('staff:staff-project-detail', kwargs={'pk': self.kwargs.get('pk')})



class TeamDetail(StaffTeamRoleMixin, DetailView):
    model = Team
    template_name = 'staff/team_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TeamDetail, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        context['staff_list'] = Staff.objects.filter(team_id = self.kwargs.get('pk'), is_deleted=False)
        return context


class TeamUpdate(StaffTeamRoleMixin, UpdateView):
    form_class = TeamForm
    model = Team
    def get_success_url(self):
        return reverse('staff:team-detail', kwargs={'pk': self.kwargs.get('pk')})






# Staff views:
class StaffList(StaffTeamRoleMixin, ListView):
    model = Staff
    template_name = 'staff/staff_list.html.html'

    # def get_context_data(self, **kwargs):
    #     context = super(StaffList, self).get_context_data(**kwargs)
    #     return context

    def get_queryset(self, request, queryset):
        queryset =  Staff.objects.filter(team_id=self.kwargs.get('pk'), is_deleted= False)
        return queryset






class StaffCreate(StaffTeamRoleMixin, CreateView):
    model = Staff
    fields = ['first_name','last_name', 'gender', 'ethnicity','address','phone_number','bank_name', 'account_number', 'photo', 'designation']
    success_url = reverse_lazy('staff:staff-list')


    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.team_id = self.kwargs.get('pk')
        return super(StaffCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('staff:team-detail', kwargs={'pk': self.kwargs.get('pk')})

class StaffDetail(StaffRoleMixin, DetailView):
    model = Staff
    template_name = 'staff/staff_detail.html'

    def get_context_data(self, **kwargs):
        context = super(StaffDetail, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        context['attendance_list'] = self.object.get_attendance()
        return context

class StaffUpdate(StaffRoleMixin, UpdateView):
    model = Staff
    form_class = StaffForm 
    success_url = reverse_lazy('staff:staff-list')

    def get_success_url(self):
        # Redirect to previous url
        next = self.request.POST.get('next', '/')
        return next



    def get_success_url(self):
        return reverse('staff:staff-detail', kwargs={'pk': self.kwargs.get('pk')})



class StaffDelete(StaffRoleMixin, DeleteView):
    model = Staff

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        staff_id = self.kwargs['pk']
        staff = Staff.objects.get(id = staff_id)
        staff.is_deleted = True
        staff.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('staff:team-detail', kwargs={'pk': self.object.team_id})
#StaffProject Views







class StaffProjectCreate(HasStaffRoleMixin, CreateView):
    model = StaffProject
    model = StaffProject
    fields = ['name',]

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(StaffProjectCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('staff:staff-project-list')

class StaffProjectList(HasStaffRoleMixin, ListView):
    model = StaffProject
    template_name = 'staff/staffproject_list.html'

    def get_context_data(self, **kwargs):
        context = super(StaffProjectList, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        queryset = StaffProject.objects.filter(is_deleted=False)
        return queryset




class StaffProjectUpdate(StaffProjectRoleMixin, UpdateView):
    model = StaffProject
    model = StaffProject
    fields = ['name',]

    def get_success_url(self):
        return reverse('staff:staff-project-detail', kwargs={'pk': self.kwargs.get('pk')})


class StaffProjectDetail(StaffProjectRoleMixin, DetailView):
    model = StaffProject
    template_name = 'staff/staffproject_detail.html'

    def get_context_data(self, **kwargs):
        context = super(StaffProjectDetail, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        context['team_list'] = Team.objects.filter(staffproject_id = self.kwargs.get('pk'), is_deleted=False)
        return context
