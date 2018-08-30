from django.shortcuts import render, get_object_or_404
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Team, Staff, StaffProject, Attendance
from onadata.apps.userrole.models import UserRole
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from onadata.apps.staff.staffrolemixin import HasStaffRoleMixin, StaffProjectTeamRoleMixin, StaffProjectRoleMixin, StaffTeamRoleMixin, StaffRoleMixin
from django.contrib.auth.models import User
from onadata.apps.staff.forms import TeamForm, StaffEditForm, StaffForm, AttendanceForm, ProjectForm
import pyexcel as p
import datetime
import calendar
from django.http import HttpResponse
import json
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

class TeamDelete(StaffProjectTeamRoleMixin, DeleteView):
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

    def get_context_data(self, **kwargs):
        context = super(TeamCreate, self).get_context_data(**kwargs)
        context['staffproject'] = StaffProject.objects.get(pk=self.kwargs.get('pk'))
        return context

    def form_valid(self, form):
        form.instance.staffproject_id = self.kwargs.get('pk')
        form.instance.created_by = self.request.user
        return super(TeamCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('staff:staff-project-detail', kwargs={'pk': self.kwargs.get('pk')})

class TeamStaffsapi(StaffTeamRoleMixin, View):
    def get(self, request, pk):
        staffs = Staff.objects.filter(team=pk).values_list('id', 'first_name', 'last_name')
        return HttpResponse(json.dumps(list(staffs)))


class TeamReAssignStaff(StaffTeamRoleMixin, View):
    def get(self, request, *args, **kwargs):
        teams=Team.objects.filter(staffproject_id=self.kwargs.get('pk')).exclude(pk=self.kwargs.get('team_id'))
        return render(request, 'staff/teamReAssignForm.html',{'teams': teams, 'obj':Team.objects.get(pk=self.kwargs.get('team_id'))})

    def post(self, request, *args, **kwargs):
        staff = get_object_or_404(Staff, pk=request.POST.get('staff_id'))
        staff.team = get_object_or_404(Team, pk=self.kwargs.get('team_id'))
        staff.save()
        return HttpResponseRedirect(reverse('staff:team-detail', kwargs={'pk': self.kwargs.get('team_id')}))


class TeamDetail(StaffTeamRoleMixin, DetailView):
    model = Team
    template_name = 'staff/team_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TeamDetail, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        
        context['is_project_manager'] = False
        user_role = self.request.roles.filter(group_id=8, staff_project_id=self.get_object().staffproject.id)
        if user_role or self.request.group.name == "Super Admin":
            context['is_project_manager'] = True
        context['staff_list'] = Staff.objects.filter(team_id = self.kwargs.get('pk'), is_deleted=False)
        context['attendance_list'] = self.object.get_attendance()
        return context

class TeamUpdate(StaffTeamRoleMixin, UpdateView):
    form_class = TeamForm
    model = Team
    def get_success_url(self):
        return reverse('staff:team-detail', kwargs={'pk': self.kwargs.get('pk')})


class TeamAttendanceReport(StaffTeamRoleMixin, View):
    def get(self, request, *args, **kwargs):
        team_id = self.kwargs.get('pk')
        year_month = self.kwargs.get('date')
        
        year = int(year_month.split('-')[0])
        month = int(year_month.split('-')[1])
        totaldays= calendar.monthrange(year,month)[1]
        monthName = calendar.month_name[month]
       
        data = []
        index_rows=["staff", "designation"]
        preheader=["",""]
        head_rows = ["Staff Name", "Designation"]
        pre_data={}
        # head_row.append(monthName + " " +str(year))
        for x in range(totaldays):
            date_day=x+1
            preheader.append(str(calendar.day_name[calendar.weekday(year, month, date_day)])[:3])
            head_rows.append(str(date_day))
            index_rows.append(str(year)+"-"+str(month).zfill(2)+"-"+str(date_day).zfill(2))
        
        team = Team.objects.get(pk=team_id, is_deleted=False)
        attendance_data = team.get_attendance_for_excel(year, month)

        data.append(["","","",""])
        data.append(["","","","", str(team.staffproject.name)])
        data.append(["","","","", str(team.name)])
        data.append(["","","","", "Attendance Report"])
        data.append(["","","","", monthName + ' ' + str(year)])
        data.append(["","","",""])
        data.append(preheader)
        data.append(head_rows)
        
        
        for staff in team.staff_team.filter(is_deleted=False):
            staff_detail = [staff.get_fullname(), staff.get_abr_designation()]
            staff_detail.extend(['A']*totaldays)
            pre_data[staff.id] = staff_detail
        
        for k,v in attendance_data.items():
            index = index_rows.index(k)
            if index:
                for staff in v:
                    if staff in pre_data:
                        pre_data[staff][index] = "P"

        for k,v in pre_data.items():
            data.append(v)
        

        p.save_as(array=data, dest_file_name="media/attendance_data.xls".format(team), sheet_name=monthName)
        xl_data = open("media/attendance_data.xls".format(team), "rb")
        response = HttpResponse(xl_data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="'+monthName+' '+ str(year) +' attendance '+team.name+'.xls"'
        return response





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
    form_class = StaffForm

    def get_context_data(self, **kwargs):
        context = super(StaffCreate, self).get_context_data(**kwargs)
        context['team'] = Team.objects.get(pk=self.kwargs.get('pk'))
        return context

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
    form_class = StaffEditForm


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
    form_class = ProjectForm

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
        context['staff_list'] = self.object.staff_project_roles.filter(ended_at = None)

        return context

class StaffProjectUsers(StaffProjectRoleMixin, TemplateView):
    template_name = 'staff/staffproject_users.html'

    def get_context_data(self, **kwargs):
        context = super(StaffProjectUsers, self).get_context_data(**kwargs)
        context['staffproject'] = StaffProject.objects.get(pk=self.kwargs.get('pk'))
        current_users = UserRole.objects.filter(staff_project_id=self.kwargs.get('pk'), ended_at = None).values('user_id')
        context['staff_list'] = UserRole.objects.filter(staff_project_id=self.kwargs.get('pk'), ended_at = None)
        context['available_user_list'] = UserRole.objects.filter(project_id__in=[183, 137, 105, 129], ended_at=None).exclude(user_id__in=current_users).distinct('user_id')
        return context

class StaffAddProjectUsers(StaffProjectRoleMixin, View):
    def get(self, request, pk, user_id, *args, **kwargs):
        staffproject_id = pk
        role = UserRole.objects.create(user_id = user_id, group_id=8, staff_project_id = staffproject_id)
        return HttpResponseRedirect(reverse('staff:staff-project-users', kwargs={'pk': staffproject_id }))

class StaffAttendanceUpdate(StaffProjectTeamRoleMixin, UpdateView):
    model = Attendance
    form_class = AttendanceForm

    def get_object(self):
        date = self.kwargs.get('date')
        team_id = self.kwargs.get('pk')
        has_attendance = Attendance.objects.filter(attendance_date=date, team_id=team_id, is_deleted=False)
        if not has_attendance:
            attendance = Attendance.objects.create(attendance_date=date, team_id=team_id, is_deleted=False, submitted_by=self.request.user)        
        else:
            attendance = has_attendance[0]
        return attendance

    def get_success_url(self):
        return reverse('staff:team-detail', kwargs={'pk': self.kwargs.get('pk')})
