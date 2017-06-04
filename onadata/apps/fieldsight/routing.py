from channels.routing import route_class
from onadata.apps.fieldsight.consumers import OneToOneConsumer, GroupConsumer, NotificationConsumer

channel_routing = [
    route_class(OneToOneConsumer, path=r"^/chat/(?P<pk>[0-9]+)/$"),
    route_class(GroupConsumer, path=r"^/groupchat/(?P<group_id>[^/]+)/$"),
    route_class(NotificationConsumer, path=r"^/notify/(?P<pk>[0-9]+)/$"),
]