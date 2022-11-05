from typing import Any, Optional

import requests
from requests.exceptions import JSONDecodeError

from kin_news_core.constants import KIN_TOKEN_PREFIX, JWT_PREFIX
from kin_news_core.exceptions import ServiceProxyError


class ServiceProxy:
    def __init__(self, jwt_token: Optional[str] = None, kin_token: Optional[str] = None):
        if not jwt_token and not kin_token:
            raise ValueError('ServiceProxy has to get at least on of jwt or kin tokens!')

        self._jwt_token = jwt_token
        self._kin_token = kin_token

        self._session = requests.Session()
        self._set_authentication_headers()

    def post(self, url: str, data: dict[str, Any]) -> dict[str, Any]:
        response = self._session.post(url, data=data, verify=False)

        if not response.ok:
            raise ServiceProxyError(f'Request to {url} failed with status: {response.status_code}')

        try:
            return response.json()
        except JSONDecodeError:
            raise ServiceProxyError(f'Request to {url} returned not a valid json with message: {response.text}')

    def _set_authentication_headers(self) -> None:
        if self._kin_token:
            self._session.headers.update({
                'HTTP_AUTHORIZATION': f'{KIN_TOKEN_PREFIX} {self._kin_token}'
            })

        self._session.headers.update({
            'HTTP_AUTHORIZATION': f'{JWT_PREFIX} {self._jwt_token}'
        })
