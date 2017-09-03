from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
import datetime

class InviteActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, invite):
        return (
            six.text_type(invite.pk) + six.text_type(datetime.datetime.now()) +
            six.text_type(invite.group.name)
        )

invite_activation_token = InviteActivationTokenGenerator()