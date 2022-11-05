from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.request import Request

from kin_news_core.constants import KIN_TOKEN_PREFIX


class KinTokenAuthentication(BaseAuthentication):
    def authenticate(self, request: Request):
        token_header = get_authorization_header(request).split()  # list of "Token" prefix and token value

        if not token_header:
            raise NotAuthenticated('Provide authentication header')
        if token_header[0].decode('utf-8').lower() != KIN_TOKEN_PREFIX:
            raise AuthenticationFailed('Invalid authentication token provided')
        if len(token_header) >= 3:
            raise AuthenticationFailed(detail='Authentication header has spaces')
        if len(token_header) == 1:
            raise AuthenticationFailed(detail='Authentication header does not contains token')

        kin_token = self._decode_token_from_header(token_header)
        if kin_token != settings.KIN_TOKEN:
            raise AuthenticationFailed('Invalid authentication token provided')

        return User.objects.get(username='root'), None

    @staticmethod
    def _decode_token_from_header(token_header: tuple[bytes, bytes]) -> str:
        return token_header[1].decode('utf-8')
