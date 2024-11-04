from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tg_token: str
    x_rapidapi_host: str
    x_rapidapi_key: str
    team_id: int = 35
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
