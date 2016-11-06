from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^set-role/(?P<pk>[0-9]+)/$', views.set_role, name='set_role'),
    url(r'^login/', views.web_login, name='web_login'),
    url(r'^alter-status/(?P<pk>[0-9]+)/$', views.alter_status, name='alter_status'),
    url(r'^api/get-auth-token/$', views.ObtainAuthToken.as_view() ),
    url(r'^profile-update/$', views.profile_update, name='profile_update'),
    ]

