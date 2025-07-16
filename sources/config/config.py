from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tg_token: str
    tg_bot_id: str
    tg_kzn_reds_chat_id: str
    sofascore_rapidapi_url: str
    x_rapidapi_host: str
    x_rapidapi_key: str
    sofascore_team_id: str = "35"
    database: str
    login: str
    password: str
    host: str
    port: str
    admin_ids: list[str]
    timedelta_to_start_sending_in_hours: str = "28"
    send_job_timeout_in_sec: str = "300"
    update_match_job_timeout_in_sec: str = "3600"
    base_team_name: str
    base_team_located_ru_name: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
