from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^login/', views.web_login, name='web_login'),
    url(r'^me/', views.current_user, name='current_user'),
    url(r'^alter-status/(?P<pk>[0-9]+)/$', views.alter_status, name='alter_status'),
    url(r'^api/get-auth-token/$', views.ObtainAuthToken.as_view() ),
    url(r'^profile-update/(?P<pk>[0-9]+)/$', views.ProfileUpdateView.as_view(), name='profile_update'),
    url(r'^profile/$', views.my_profile, name='profile'),
    ]

