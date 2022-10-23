from dependency_injector import resources

from kin_news_core.telegram.client import TelegramClientProxy


class TelegramProxyResource(resources.Resource):
    def init(self, api_id: int, api_hash: str) -> TelegramClientProxy:
        return TelegramClientProxy.from_api_config(api_id, api_hash)
