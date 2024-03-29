from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class TelegramSettings(BaseSettings):
    api_id: int = Field(..., validation_alias="TELEGRAM_API_ID")
    api_hash: str = Field(..., validation_alias="TELEGRAM_API_HASH")
    session_string: str = Field(..., validation_alias="TELEGRAM_SESSION_STRING")


class Settings(BaseSettings):
    secret_key: str = Field(..., validation_alias="SECRET_KEY")
    log_level: str = Field("INFO", validation_alias="LOG_LEVEL")
    debug: bool = Field(False, validation_alias="DEBUG")
    kin_token: str = Field(..., validation_alias="KIN_TOKEN")
    statistics_service: str = Field(..., validation_alias="STATISTICS_SERVICE_URL")
    rabbitmq_connection_string: str = Field(..., validation_alias="RABBITMQ_CONNECTION_STRING")
    model_types_service_url: str = Field(..., validation_alias="MODEL_TYPES_SERVICE_URL")

    rabbitmq_queue_name: str | None = Field(None, validation_alias="RABBITMQ_QUEUE_NAME")

    model_config = ConfigDict(protected_namespaces=("settings_",))
