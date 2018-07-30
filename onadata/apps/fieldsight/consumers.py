from channels import Group
from channels.generic.websockets import WebsocketConsumer


class OrganizationAdminConsumer(WebsocketConsumer):

    # Set to True to automatically port users from HTTP cookies
    # (you don't need channel_session_user, this implies it)

    # Set to True if you want it, else leave it out
    strict_ordering = False

    def connection_groups(self, **kwargs):
        """
        Called to return the list of groups to automatically add/remove
        this connection to/from.
        """
        pk = kwargs.get('pk')
        return ["org-notify-"+pk]

    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        # Accept the connection; this is done by default if you don't override
        # the connect function.
        # make this user online
        pk = kwargs.get('pk')
        Group("org-notify-"+pk).add(message.reply_channel)
        self.message.reply_channel.send({"accept": True})

    def disconnect(self, message, **kwargs):
        pk = kwargs.get('pk')
        Group("org-notify-"+pk).discard(message.reply_channel)


class SuperAdminConsumer(WebsocketConsumer):

    # Set to True to automatically port users from HTTP cookies
    # (you don't need channel_session_user, this implies it)

    # Set to True if you want it, else leave it out
    strict_ordering = False

    def connection_groups(self, **kwargs):
        """
        Called to return the list of groups to automatically add/remove
        this connection to/from.
        """
        pk = kwargs.get('pk')
        return ["user-notify-"+pk]

    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        # Accept the connection; this is done by default if you don't override
        # the connect function.
        # make this user online
        pk = kwargs.get('pk')
        Group("user-notify-"+pk).add(message.reply_channel)
        self.message.reply_channel.send({"accept": True})

    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        # make this user offline
        pk = kwargs.get('pk')
        Group("user-notify-"+pk).discard(message.reply_channel)


class ProjectLevelConsumer(WebsocketConsumer):

    strict_ordering = False

    def connection_groups(self, **kwargs):
        pk = kwargs.get('pk')
        return ["project-notify-"+pk]

    def connect(self, message, **kwargs):

        pk = kwargs.get('pk')
        Group("project-notify-"+pk).add(message.reply_channel)
        self.message.reply_channel.send({"accept": True})

    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        # make this user offline
        pk = kwargs.get('pk')
        Group("project-notify-"+pk).discard(message.reply_channel)
