from django.shortcuts import render, get_object_or_404
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Team, Staff
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect


# Team views:
class TeamList(ListView):
    model = Team
    template_name = 'staff/team_list.html'

    def get_context_data(self, **kwargs):
        # pass
        context = super(TeamList, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        context['team_list'] = Team.objects.filter(is_deleted= False)
        return context


class TeamDetail(DetailView):
    model = Team
    template_name = 'staff/team_detail.html'



class TeamCreate(CreateView):
    model = Team
    fields = ['leader','name','created_by']
    success_url = reverse_lazy('staff:team-list')


class TeamUpdate(UpdateView):
    model = Team
    fields = ['leader','name','created_by']
    success_url = reverse_lazy('staff:team-list')


class TeamDelete(DeleteView):
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
class StaffList(ListView):
    model = Staff
    template_name = 'staff/staff_list.html.html'

    def get_context_data(self, **kwargs):
        context = super(StaffList, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        context['staff_list.html'] = Staff.objects.filter(is_deleted= False)
        return context


class StaffDetail(DetailView):
    model = Staff
    template_name = 'staff/staff_detail.html'


class StaffCreate(CreateView):
    model = Staff
    fields = ['first_name','last_name', 'gender', 'ethnicity','address','phone_number','bank_name', 'account_number', 'photo', 'designation','created_by']
    success_url = reverse_lazy('staff:staff-list')


class StaffUpdate(UpdateView):
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