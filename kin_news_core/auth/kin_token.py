from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request


class KinTokenAuthentication(BaseAuthentication):
    def authenticate(self, request: Request):
        kin_token = request.data.dict().get('token')

        if kin_token != settings.KIN_TOKEN:
            raise AuthenticationFailed('Invalid authentication token provided')

        return User(), None

    @staticmethod
    def _decode_token_from_header(token_header: tuple[bytes, bytes]) -> str:
        return token_header[1].decode('utf-8')
