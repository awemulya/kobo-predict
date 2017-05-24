from django.conf.urls import url


def notifications(args):
    pass


urlpatterns = [
    url(r'^notification/$', notifications, name='notification-list'),
    url(r'^notification/$', notifications, name='notification-list'),
    url(r'^message/(?P<pk>[0-9]+)/$', notifications, name='message-detail'),
    url(r'^notification/(?P<pk>[0-9]+)/$', notifications, name='message-detail'),
    ]