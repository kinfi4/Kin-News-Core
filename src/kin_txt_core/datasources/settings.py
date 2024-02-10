from pydantic import Field
from pydantic_settings import BaseSettings


class TelegramSettings(BaseSettings):
    api_id: int = Field(..., validation_alias="TELEGRAM_API_ID")
    api_hash: str = Field(..., validation_alias="TELEGRAM_API_HASH")
    session_string: str = Field(..., validation_alias="TELEGRAM_SESSION_STRING")


class RedditSettings(BaseSettings):
    client_id: str = Field(..., validation_alias="REDDIT_CLIENT_ID")
    client_secret: str = Field(..., validation_alias="REDDIT_CLIENT_SECRET")
    user_agent: str = Field(..., validation_alias="REDDIT_USER_AGENT")

    max_posts_per_request: int = Field(20_000, validation_alias="REDDIT_MAX_POSTS_PER_REQUEST")
