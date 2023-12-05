from typing import Any

from requests import JSONDecodeError, Response

from kin_txt_core.constants import USERNAME_HEADER
from kin_txt_core.exceptions import ServiceProxyNotFoundError, ServiceProxyDuplicateError
from kin_txt_core.service_proxy import ServiceProxy, ServiceProxyError
from kin_txt_core.reports_building.domain.entities import CustomModelRegistrationEntity


class ModelTypesService(ServiceProxy):
    def __init__(self, url: str, kin_token: str | None = None, jwt_token: str | None = None) -> None:
        super().__init__(jwt_token=jwt_token, kin_token=kin_token)
        self._base_url = url

    def get_model_binaries(self, username: str, model_code: str) -> bytes:
        target_url = f"{self._base_url}/blobs/get-model-binaries/{model_code}"
        return self._make_get_request(username=username, target_url=target_url)

    def get_tokenizer_binaries(self, username: str, model_code: str) -> bytes:
        target_url = f"{self._base_url}/blobs/get-tokenizer-binaries/{model_code}"
        return self._make_get_request(username=username, target_url=target_url)

    def get_visualization_template(self, username: str, template_id: str) -> dict:
        target_url = f"{self._base_url}/blobs/visualization-template/{template_id}"
        return self._make_get_request(username=username, target_url=target_url)

    def get_model_metadata(self, username: str, model_code: str) -> dict:
        target_url = f"{self._base_url}/models/{model_code}"
        return self._make_get_request(username=username, target_url=target_url)

    def get_visualization_templates(self, username: str, template_id: str) -> dict:
        target_url = f"{self._base_url}/visualization-template/{template_id}"
        return self._make_get_request(username=username, target_url=target_url)

    def register_model_type(self, model: CustomModelRegistrationEntity) -> dict[str, Any]:
        data = model.dict(by_alias=True)
        target_url = f"{self._base_url}/models/register"

        return self._make_post_request(username=model.owner_username, target_url=target_url, data=data)

    def _make_get_request(self, username: str, target_url: str) -> dict | bytes:
        self._session.headers.update({USERNAME_HEADER: username})

        response = self._session.get(url=target_url)

        return self._handle_response(response)

    def _make_post_request(self, username: str, target_url: str, data: dict[str, Any]) -> dict[str, Any]:
        self._session.headers.update({USERNAME_HEADER: username})

        response = self._session.post(url=target_url, json=data)

        return self._handle_response(response)

    def _handle_response(self, response: Response) -> dict[str, Any] | bytes:
        if not response.ok:
            try:
                message = response.json()
            except JSONDecodeError:
                message = response.text

            self._logger.warning(
                f'[ModelTypesService] '
                f'Request to {response.url} failed with status: {response.status_code} with message: {message}.'
            )

            if response.status_code == 404:
                raise ServiceProxyNotFoundError(f'Request to {response.url} failed with status: {response.status_code}')
            elif response.status_code == 409:
                raise ServiceProxyDuplicateError(f'Request to {response.url} failed with status: {response.status_code}')
            else:
                raise ServiceProxyError(f'Request to {response.url} failed with status: {response.status_code}')

        return response.json() if response.headers.get("Content-Type") == "application/json" else response.content
