import logging
from typing import Any, Optional

import requests
from requests.exceptions import JSONDecodeError

from kin_news_core.constants import KIN_TOKEN_PREFIX, JWT_PREFIX
from kin_news_core.exceptions import ServiceProxyError


class ServiceProxy:
    def __init__(self, jwt_token: Optional[str] = None, kin_token: Optional[str] = None):
        if not jwt_token and not kin_token:
            raise ValueError('ServiceProxy has to get at least on of jwt or kin tokens!')

        self._logger = logging.getLogger(self.__class__.__name__)

        self._jwt_token = jwt_token
        self._kin_token = kin_token

        self._session = requests.Session()
        self._set_authentication_headers()

    def post(self, url: str, data: dict[str, Any]) -> dict[str, Any]:
        response = self._session.post(url, data=data)

        if not response.ok:
            try:
                message = response.json()
            except JSONDecodeError:
                message = response.text

            self._logger.error(f'Request to {url} failed with status: {response.status_code} with message: {message}')
            raise ServiceProxyError(f'Request to {url} failed with status: {response.status_code}')

        return response.json()

    def _set_authentication_headers(self) -> None:
        if self._kin_token:
            self._session.headers.update({
                'Authorization': f'{KIN_TOKEN_PREFIX} {self._kin_token}'
            })
            return

        self._session.headers.update({
            'Authorization': f'{JWT_PREFIX} {self._jwt_token}'
        })
