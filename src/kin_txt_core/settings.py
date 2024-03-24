from pydantic import Field
from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    host: str = Field(..., validation_alias="DATABASE_HOST")
    port: int = Field(5432, validation_alias="DATABASE_PORT")
    db_name: str = Field(..., validation_alias="DATABASE_NAME")
    user: str = Field(..., validation_alias="DATABASE_USER")
    password: str = Field(..., validation_alias="DATABASE_PASSWORD")

    db_schema: str = Field("public", validation_alias="DATABASE_SCHEMA")


class AuthSettings(BaseSettings):
    secret_key: str = Field(..., validation_alias="SECRET_KEY")
    token_life_minutes: int = Field(12*60, validation_alias="TOKEN_LIFE_MINUTES")


class RedisSettings(BaseSettings):
    host: str = Field(..., validation_alias="REDIS_HOST")
    port: int = Field(6379, validation_alias="REDIS_PORT")
    photo_db_name: int = Field(None, validation_alias="REDIS_PHOTO_DB_NAME")
    channel_db_name: int = Field(None, validation_alias="REDIS_CHANNELS_DB")
