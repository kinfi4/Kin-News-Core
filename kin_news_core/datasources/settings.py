from pydantic import BaseSettings, Field


class TelegramSettings(BaseSettings):
    api_id: int = Field(..., env="TELEGRAM_API_ID")
    api_hash: str = Field(..., env="TELEGRAM_API_HASH")
    session_string: str = Field(..., env="TELEGRAM_SESSION_STRING")
