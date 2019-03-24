from django.conf.urls import url

from .views import subscribe_view, stripe_webhook, TeamSettingsView, update_card

urlpatterns = [
    url(r'^thanks/(?P<org_id>\d+)/$', subscribe_view, name='subscribe'),
    url(r'^stripe/webhook/', stripe_webhook, name='stripe_webhook'),
    url(r'^update-card/$', update_card, name='update_card'),
    url(r'^team-settings/(?P<org_id>\d+)/$', TeamSettingsView.as_view(), name='team_settings'),


]