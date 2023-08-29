from requests import JSONDecodeError

from kin_news_core.constants import USERNAME_HEADER
from kin_news_core.service_proxy import ServiceProxy, ServiceProxyError


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

    def _make_get_request(self, username: str, target_url: str) -> dict | bytes:
        self._session.headers.update({USERNAME_HEADER: username})

        response = self._session.get(url=target_url)

        if not response.ok:
            try:
                message = response.json()
            except JSONDecodeError:
                message = response.text

            self._logger.error(
                f'[ModelTypesService] '
                f'Request to {target_url} failed with status: {response.status_code} with message: {message}.'
            )

            raise ServiceProxyError(f'Request to {target_url} failed with status: {response.status_code}')

        return response.json() if response.headers.get("Content-Type") == "application/json" else response.content
