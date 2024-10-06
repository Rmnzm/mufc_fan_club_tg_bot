from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tg_token: str
    database: str
    login: str
    password: str
    host: str
    port: str

    class Config:
        env_file = '.env'


@lru_cache()
def get_settings():
    return Settings()
