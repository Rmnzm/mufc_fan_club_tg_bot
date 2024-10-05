from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tg_token: str
    accessed_users: str

    class Config:
        env_file = '.env'


@lru_cache()
def get_settings():
    return Settings()
