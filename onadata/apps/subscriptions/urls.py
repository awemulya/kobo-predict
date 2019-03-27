from django.conf.urls import url

from .views import subscribe_view, stripe_webhook, TeamSettingsView, update_card, finish_subscription, get_package

urlpatterns = [
    # url(r'^thanks/(?P<org_id>\d+)/$', subscribe_view, name='subscribe_old'),
    url(r'^stripe/webhook/', stripe_webhook, name='stripe_webhook'),
    url(r'^update-card/$', update_card, name='update_card'),
    url(r'^thanks/(?P<org_id>\d+)/$', subscribe_view, name='subscribe'),
    url(r'^finish/(?P<org_id>\d+)/$', finish_subscription, name='finish_subscription'),
    url(r'^ajax/get-package/$', get_package, name='get_package'),

    url(r'^team-settings/(?P<org_id>\d+)/$', TeamSettingsView.as_view(), name='team_settings'),


]