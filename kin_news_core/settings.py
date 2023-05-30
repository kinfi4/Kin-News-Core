from pydantic import BaseSettings, Field


class PostgresSettings(BaseSettings):
    host: str = Field(..., env='DATABASE_HOST')
    port: int = Field(5432, env='DATABASE_PORT')
    db_name: str = Field(..., env='DATABASE_NAME')
    user: str = Field(..., env='DATABASE_USER')
    password: str = Field(..., env='DATABASE_PASSWORD')


class CoreSettings(BaseSettings):
    secret_key: str = Field(..., env='SECRET_KEY')
    token_life_minutes: int = Field(..., env='TOKEN_LIFE_MINUTES')

    postgres: PostgresSettings = PostgresSettings()


class TelegramSettings(BaseSettings):
    api_id: int = Field(..., env='TELEGRAM_API_ID')
    api_hash: str = Field(..., env='TELEGRAM_API_HASH')
    session_string: str = Field(..., env='TELEGRAM_SESSION_STRING')
