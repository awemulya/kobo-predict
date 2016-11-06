from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from django.utils.translation import ugettext_lazy as _


def validateEmail( email ):
    from django.core.validators import validate_email
    try:
        validate_email( email )
        try:
            user = User.objects.get(email__iexact=email)
            return True
        except:
            raise ValidationError("Email not in use")
    except ValidationError:
        return False


class AuthCustomTokenSerializer(serializers.Serializer):
    email_or_username = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email_or_username = attrs.get('email_or_username')
        password = attrs.get('password')

        if email_or_username and password:
            # Check if user sent email
            if validateEmail(email_or_username):
                user_request = get_object_or_404(
                    User,
                    email=email_or_username,
                )

                email_or_username = user_request.username

            user = authenticate(username=email_or_username, password=password)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise ValidationError(msg)
            else:
                msg = _('Unable to log in with provided credentials.')
                raise ValidationError(msg)
        else:
            msg = _('Must include "email or username" and "password"')
            raise ValidationError(msg)

        attrs['user'] = user
        return attrs