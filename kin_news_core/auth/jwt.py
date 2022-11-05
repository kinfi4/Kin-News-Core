from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.request import Request

from kin_news_core.constants import JWT_PREFIX


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request: Request):
        if 'docs/' in request._request.path:  # I added this line, in order to user swagger docs without authentication
            return User.objects.all()[0], None

        token_header = get_authorization_header(request).split()  # list of "Token" prefix and token value

        if not token_header:
            raise NotAuthenticated('Provide authentication header')
        if token_header[0].decode('utf-8').lower() != JWT_PREFIX:
            raise AuthenticationFailed('Invalid authentication token provided')
        if len(token_header) >= 3:
            raise AuthenticationFailed(detail='Authentication header has spaces')
        if len(token_header) == 1:
            raise AuthenticationFailed(detail='Authentication header does not contains token')

        token = token_header[1].decode('utf-8')
        return self._get_authenticated_user(token), None

    @staticmethod
    def _get_authenticated_user(token: str) -> User:
        try:
            decoded_token = jwt.decode(token, algorithms='HS256', key=settings.SECRET_KEY)
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid symbols passed in auth token')

        if datetime.utcnow() > datetime.fromtimestamp(decoded_token['exp']):
            raise AuthenticationFailed('Authentication token expired')

        try:
            return User.objects.get(username=decoded_token['username'])
        except ObjectDoesNotExist:
            raise AuthenticationFailed('User for provided token does not exists')


def create_jwt_token(username) -> str:
    token_duration = timedelta(minutes=settings.TOKEN_LIFE_MINUTES)
    token_expiration_time = datetime.utcnow() + token_duration

    to_encode = {'username': username, 'exp': token_expiration_time, 'sub': 'access'}

    encoded_token = jwt.encode(to_encode, algorithm='HS256', key=settings.SECRET_KEY)

    return encoded_token
