from channels.routing import route_class
from onadata.apps.fieldsight.consumers import SuperAdminConsumer,OrganizationAdminConsumer, ProjectLevelConsumer

channel_routing = [
    route_class(SuperAdminConsumer, path=r"^/user-notify/(?P<pk>[0-9]+)/$"),
    route_class(OrganizationAdminConsumer, path=r"^/org-notify/(?P<pk>[0-9]+)/$"),
    route_class(ProjectLevelConsumer, path=r"^/project-notify/(?P<pk>[0-9]+)/$"),
]
