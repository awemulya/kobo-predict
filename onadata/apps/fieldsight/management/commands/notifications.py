import json
from django.core.management.base import BaseCommand
from channels import Group as ChannelGroup



class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **options):
        result = {
            "id": 45639,
            "source_uid": 147,
            "source_name": "Kiran Shrestha",
            "source_img": "/media/logo/default_user.png",
            "get_source_url": "/users/profile/147/",
            "get_event_name": "staged form Ring Beam",
            "get_event_url": "/forms/forms/31523",
            "get_extraobj_name": "TestHouse",
            "get_extraobj_url": "/fieldsight/site-dashboard/4119/",
            "get_absolute_url": "/events/notification/45639/",
            "extra_json": '',
            "type": 16,
            "title": "new Site level Submission",
            "date": "2018-07-17T11:13:41.440880Z",
            "extra_message": '',
            "recipient": '',
            "seen_by": []
        },
        # ChannelGroup("notify-{}".format(1)).send({"text": json.dumps(result)})
        ChannelGroup("user-notify-{}".format(1)).send({"text": json.dumps(result)})
        ChannelGroup("org-notify-{}".format(1)).send({"text": json.dumps(result)})
        ChannelGroup("project-notify-{}".format(1)).send({"text": json.dumps(result)})
        self.stdout.write('Successfully created Notification')