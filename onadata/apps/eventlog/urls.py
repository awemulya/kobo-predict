from django.conf.urls import url

from onadata.apps.eventlog.views import NotificationListView, NotificationCountnSeen, NotificationViewSet, NotificationDetailView, MessageListView
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
    ]