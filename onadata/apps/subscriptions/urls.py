from django.conf.urls import url

from .views import subscribe_view, stripe_webhook

urlpatterns = [
    url(r'^thanks/(?P<org_id>\d+)/$', subscribe_view, name='subscribe'),
    url(r'^stripe/webhook/', stripe_webhook, name='stripe_webhook'),

]