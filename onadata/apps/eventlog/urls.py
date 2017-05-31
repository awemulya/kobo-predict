from django.conf.urls import url

from onadata.apps.eventlog.views import NotificationListView


def notifications(args):
    pass


urlpatterns = [
    url(r'^notification/$', NotificationListView.as_view(), name='notification-list'),
    url(r'^message/$', notifications, name='message-list'),
    url(r'^notification/(?P<pk>[0-9]+)/$', notifications, name='notification-detail'),
    url(r'^message/(?P<pk>[0-9]+)/$', notifications, name='message-detail'),
    ]