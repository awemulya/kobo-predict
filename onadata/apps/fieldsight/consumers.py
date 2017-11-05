from channels import Group
from channels.generic.websockets import WebsocketConsumer, WebsocketDemultiplexer


class GroupConsumer(WebsocketConsumer):

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
        return ["chat-"+pk]

    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        # Accept the connection; this is done by default if you don't override
        # the connect function.
        pk = kwargs.get('pk')
        self.message.reply_channel.send({"accept": True})

    def receive(self, text=None, bytes=None, **kwargs):
        """
        Called when a message is received with either text or bytes
        filled out.
        """
        # Simple echo
        pk = kwargs.get('pk')
        self.send(text=text, bytes=bytes)

    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        pass


class OneToOneConsumer(WebsocketConsumer):

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
        return ["chat-"+pk]

    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        # Accept the connection; this is done by default if you don't override
        # the connect function.
        # make this user online
        pk = kwargs.get('pk')
        Group("chat-"+pk).add(message.reply_channel)
        self.message.reply_channel.send({"accept": True})

    def receive(self, text=None, bytes=None, **kwargs):
        """
        Called when a message is received with either text or bytes
        filled out.
        """
        # Simple echo
        pk = kwargs.get('pk')
        print text
        receiver_pk = pk
        # get receiver-id send it to group chat-receiverid
        Group("chat-"+receiver_pk).send({
        "text": text})
        self.send(text=text, bytes=bytes)

    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        # make this user offline
        pk = kwargs.get('pk')
        Group("chat-"+pk).discard(message.reply_channel)


class OneToOneNotifConsumer(WebsocketConsumer):

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
        return ["notif-user-"+pk]

    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        # Accept the connection; this is done by default if you don't override
        # the connect function.
        # make this user online
        pk = kwargs.get('pk')
        Group("notif-user-"+pk).add(message.reply_channel)
        self.message.reply_channel.send({"accept": True})

    def receive(self, text=None, bytes=None, **kwargs):
        """
        Called when a message is received with either text or bytes
        filled out.
        """
        # Simple echo
        pk = kwargs.get('pk')
        print text
        receiver_pk = pk
        # get receiver-id send it to group chat-receiverid
        Group("notif-user-"+receiver_pk).send({
        "text": text})
        self.send(text=text, bytes=bytes)

    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        # make this user offline
        pk = kwargs.get('pk')
        Group("notif-user-"+pk).discard(message.reply_channel)


class NotificationConsumer(WebsocketConsumer):

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
        return ["notify-"+pk]

    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        # Accept the connection; this is done by default if you don't override
        # the connect function.
        pk = kwargs.get('pk')
        Group("notify-{}".format(pk)).add(message.reply_channel)
        self.message.reply_channel.send({"accept": True})

    def receive(self, text=None, bytes=None, **kwargs):
        """
        Called when a message is received with either text or bytes
        filled out.
        """
        # Simple echo
        pk = kwargs.get('pk')
        print text
        print bytes
        self.send(text=text, bytes=bytes)

    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        pk = kwargs.get('pk')
        Group("notify-{}".format(pk)).discard(message.reply_channel)


class ProjectLevelConsumer(WebsocketConsumer):

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
        return ["notify-project-"+pk]

    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        # Accept the connection; this is done by default if you don't override
        # the connect function.
        pk = kwargs.get('pk')
        Group("notify-project-{}".format(pk)).add(message.reply_channel)
        self.message.reply_channel.send({"accept": True})

    def receive(self, text=None, bytes=None, **kwargs):
        """
        Called when a message is received with either text or bytes
        filled out.
        """
        # Simple echo
        pk = kwargs.get('pk')
        print text
        print bytes
        self.send(text=text, bytes=bytes)

    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        pk = kwargs.get('pk')
        Group("notify-project-{}".format(pk)).discard(message.reply_channel)


class SiteLevelConsumer(WebsocketConsumer):

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
        return ["notify-site-"+pk]

    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        # Accept the connection; this is done by default if you don't override
        # the connect function.
        pk = kwargs.get('pk')
        Group("notify-site-{}".format(pk)).add(message.reply_channel)
        self.message.reply_channel.send({"accept": True})

    def receive(self, text=None, bytes=None, **kwargs):
        """
        Called when a message is received with either text or bytes
        filled out.
        """
        # Simple echo
        pk = kwargs.get('pk')
        print text
        print bytes
        self.send(text=text, bytes=bytes)

    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        pk = kwargs.get('pk')
        Group("notify-site-{}".format(pk)).discard(message.reply_channel)


# class Demultiplexer(WebsocketDemultiplexer):
#
#     # Wire your JSON consumers here: {stream_name : consumer}
#     consumers = {
#         "single": OneToOneConsumer,
#         "group": GroupConsumer,
#     }