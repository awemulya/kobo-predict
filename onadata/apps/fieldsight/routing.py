from channels.routing import route
from onadata.apps.fieldsight.consumers import ws_message

channel_routing = [
    route("websocket.receive", ws_message),
]