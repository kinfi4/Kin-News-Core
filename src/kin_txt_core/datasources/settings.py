from pydantic import BaseSettings, Field


class TelegramSettings(BaseSettings):
    api_id: int = Field(..., env="TELEGRAM_API_ID")
    api_hash: str = Field(..., env="TELEGRAM_API_HASH")
    session_string: str = Field(..., env="TELEGRAM_SESSION_STRING")


class RedditSettings(BaseSettings):
    client_id: str = Field(..., env="REDDIT_CLIENT_ID")
    client_secret: str = Field(..., env="REDDIT_CLIENT_SECRET")
    user_agent: str = Field(..., env="REDDIT_USER_AGENT")

    max_posts_per_request: int = Field(20_000, env="REDDIT_MAX_POSTS_PER_REQUEST")
