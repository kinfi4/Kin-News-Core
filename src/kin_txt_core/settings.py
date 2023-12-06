from pydantic import Field, BaseSettings


class PostgresSettings(BaseSettings):
    host: str = Field(..., env="DATABASE_HOST")
    port: int = Field(5432, env="DATABASE_PORT")
    db_name: str = Field(..., env="DATABASE_NAME")
    user: str = Field(..., env="DATABASE_USER")
    password: str = Field(..., env="DATABASE_PASSWORD")


class AuthSettings(BaseSettings):
    secret_key: str = Field(..., env="SECRET_KEY")
    token_life_minutes: int = Field(12*60, env="TOKEN_LIFE_MINUTES")


class RedisSettings(BaseSettings):
    host: str = Field(..., env="REDIS_HOST")
    port: int = Field(6379, env="REDIS_PORT")
    photo_db_name: int = Field(None, env="REDIS_PHOTO_DB_NAME")
    channel_db_name: int = Field(None, env="REDIS_CHANNELS_DB")
