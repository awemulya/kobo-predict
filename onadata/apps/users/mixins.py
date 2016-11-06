from kpi.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class OwnProfileRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        # get user object and check with request obj
        if not request.user:
            raise PermissionDenied()
        return super(OwnProfileRequiredMixin, self).dispatch(request, *args, **kwargs)


class OwnProfileView(OwnProfileRequiredMixin):
    def get_queryset(self):
        return super(OwnProfileView, self).get_queryset().filter(user=self.request.user)



