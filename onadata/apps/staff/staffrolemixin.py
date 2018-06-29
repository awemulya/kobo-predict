from django.contrib.auth.models import User





from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView

from onadata.apps.staff.models import Staff, Team, StaffProject
from onadata.apps.userrole.models import UserRole
from django.shortcuts import get_object_or_404

from django.db.models import Q



# Important , in near future roles should be cached or some similar alternatives should be added.

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwargs):
        view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        return login_required(view)

class HasStaffRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(HasStaffRoleMixin, self).dispatch(request, *args, **kwargs)
        
        # user_role = request.roles.filter(group_id=8)
        # if user_role:
        #     return super(HasStaffRoleMixin, self).dispatch(request, *args, **kwargs)
        # raise PermissionDenied()


class StaffProjectRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(StaffProjectRoleMixin, self).dispatch(request, *args, **kwargs)
        staff_project_id = self.kwargs.get('pk')
        user_role = request.roles.filter(group_id=8, staff_project_id=staff_project_id)
        if user_role:
            return super(StaffProjectRoleMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()

class StaffProjectTeamRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(StaffProjectTeamRoleMixin, self).dispatch(request, *args, **kwargs)
        staff_team_id = self.kwargs.get('pk')
        staff_project_id = get_object_or_404(Team, pk=staff_team_id).staffproject_id
        user_role = request.roles.filter(group_id=8, staff_project_id=staff_project_id)
        if user_role:
            return super(StaffProjectTeamRoleMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()

class StaffTeamRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(StaffTeamRoleMixin, self).dispatch(request, *args, **kwargs)

        team = get_object_or_404(Team, pk=self.kwargs.get('pk'))        
        
        if team.is_deleted:
            raise PermissionDenied()

        if int(team.leader_id) == int(request.user.id):
            return super(StaffTeamRoleMixin, self).dispatch(request, *args, **kwargs)
        
        user_role = request.roles.filter(group_id=8, staff_project_id=team.staffproject.id)
        if user_role:
            return super(StaffTeamRoleMixin, self).dispatch(request, *args, **kwargs)
        
        raise PermissionDenied()


class StaffRoleMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.group.name == "Super Admin":
            return super(StaffRoleMixin, self).dispatch(request, *args, **kwargs)

        staff = get_object_or_404(Staff, pk=self.kwargs.get('pk'))
        
        if staff.is_deleted:
            raise PermissionDenied()
    
        if staff.team.leader_id == request.user.id:
            return super(StaffRoleMixin, self).dispatch(request, *args, **kwargs)
        
        user_role = request.roles.filter(group_id=8, staff_project_id=staff.team.staffproject.id)
        if user_role:
            return super(StaffRoleMixin, self).dispatch(request, *args, **kwargs)
        
        raise PermissionDenied()
