from django.conf.urls import url

from onadata.apps.eventlog.views import ProjectLogListView, OtherTaskListViewSet,  MyTaskListViewSet, SiteLogListView, SiteLog, ProjectLog, CeleryTaskProgressView, MyCeleryTaskProgress, NotificationListView, NotificationCountnSeen, NotificationViewSet, NotificationDetailView, MessageListView
from onadata.apps.fieldsight.mixins import group_required


@group_required("hello")
def notifications(args):
    pass


urlpatterns = [
    url(r'^notification/$', NotificationListView.as_view(), name='notification-list'),
    url(r'^api/notification/$', NotificationViewSet.as_view({'get': 'list'}), name="api-not"),
    url(r'^api/notification/count/$', NotificationCountnSeen.as_view(), name="api-not-count"),
    url(r'^message/$', MessageListView.as_view(), name='message-list'),
    url(r'^notification/(?P<pk>[0-9]+)/$', NotificationDetailView.as_view(), name='notification-detail'),
    url(r'^message/(?P<pk>[0-9]+)/$', notifications, name='message-detail'),
    url(r'^task_state$', CeleryTaskProgressView.as_view(), name="task_state"),

    url(r'^mytasks_progress$', MyCeleryTaskProgress.as_view(), name="mytasks_progress"),
    url(r'^api/project_logs/(?P<pk>[0-9]+)/$', ProjectLog.as_view({'get': 'list'}), name="api_project_logs"),
    url(r'^api/site_logs/(?P<pk>[0-9]+)/$', SiteLog.as_view({'get': 'list'}), name="api_site_logs"),

    url(r'^project_logs/(?P<pk>[0-9]+)/$', ProjectLogListView.as_view(), name="project_logs"),
    url(r'^site_logs/(?P<pk>[0-9]+)/$', SiteLogListView.as_view(), name="site_logs"),
    url(r'^api/mytasks/$', MyTaskListViewSet.as_view({'get': 'list'}), name="my_task_list"),
    url(r'^api/othertasks/$', OtherTaskListViewSet.as_view({'get': 'list'}), name="other_task_list")

    ]
