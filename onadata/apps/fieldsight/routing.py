from channels.routing import route
channel_routing = [
    route("http.request", "onadata.apps.fieldsight.consumers.http_consumer"),
]