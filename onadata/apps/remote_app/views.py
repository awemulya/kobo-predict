from django.utils import timezone
from django.utils.six import text_type
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import (
    views,
    response,
    authentication,
    exceptions,
    HTTP_HEADER_ENCODING,
)
import jwt

from onadata.apps.fieldsight.models import Site
from .models import RemoteApp, ConnectedDomain, ConnectedProject
from .serializers import SiteSerializer


AUTH_HEADER_TYPE_BYTES = 'Bearer'.encode(HTTP_HEADER_ENCODING)


class RemoteAppAuthentication(authentication.BaseAuthentication):
    def authenticate_header(self, request):
        """
        Value of www-authenticate header in 401 error
        """
        return 'Bearer realm=api'

    def authenticate(self, request):
        header = request.META.get('HTTP_AUTHORIZATION')
        if header is None:
            return None

        # Following two lines is needed for test client
        if isinstance(header, text_type):
            header = header.encode(HTTP_HEADER_ENCODING)

        parts = header.split()

        # No Bearer header at all
        if parts[0] != AUTH_HEADER_TYPE_BYTES:
            return None

        # Improper Bearer header
        if len(parts) != 2:
            raise exceptions.AuthenticationFailed(
                'Authorization header must be of format: Bearer <token>'
            )

        token = parts[1]
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithm='HS256',
        )

        user_id = payload.get('userId')
        if not user_id:
            raise exceptions.AuthenticationFailed(
                'User Id not present in token'
            )

        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                'User not found'
            )

        try:
            remote_app = RemoteApp.objects.get(token=token)
        except RemoteApp.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                'Application not found'
            )

        if remote_app.auth_user != user:
            raise exceptions.AuthenticationFailed(
                'Application not found'
            )

        domain = request.META.get('HTTP_ORIGIN') or \
            request.META.get('ORIGINAL_HTTP_REFERER') or \
            request.META.get('HTTP_REFERRER')
        if not domain or not ConnectedDomain.objects.filter(
            app=remote_app,
            domain=domain,
        ).exists():
            raise exceptions.AuthenticationFailed(
                'Domain not allowed'
            )

        return user, remote_app


class RemoteProjectView(views.APIView):
    authentication_classes = [RemoteAppAuthentication]

    def get(self, request, project_key):
        connected_project = ConnectedProject.objects.filter(
            app=request.auth,
            key=project_key,
        ).first()

        if not connected_project:
            raise exceptions.NotFound('Project not found')

        if connected_project.updated_at:
            last_timestamp = request.GET.get('last_timestamp')
            updated_timestamp = connected_project.updated_at.strftime('%s')
            if last_timestamp and \
                    updated_timestamp <= last_timestamp:
                return response.Response({
                    'updated': False,
                    'timestamp': timezone.now().strftime('%s'),
                })

        sites = Site.objects.filter(
            project=connected_project.project,
        )
        data = SiteSerializer(
            sites,
            many=True,
        ).data

        return response.Response({
            'updated': True,
            'data': data,
            'timestamp': timezone.now().strftime('%s'),
        })
