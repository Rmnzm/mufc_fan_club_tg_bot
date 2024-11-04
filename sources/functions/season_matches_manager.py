import logging

import requests

from schemes.matchday_dto import MatchDayDTO
from config.config import get_settings

settings = get_settings()

logger = logging.getLogger(__name__)


class SeasonMatchesManager:
    def __init__(self):
        pass

    def get_next_matches(self):
        response = requests.get(
            f"https://sofascore.p.rapidapi.com/teams/get-next-matches?teamId={settings.team_id}&pageIndex=0",
            headers={
                "x-rapidapi-host": settings.x_rapidapi_host,
                "x-rapidapi-key": settings.x_rapidapi_key,
            }
        )
        if response.status_code == 200:
            return self.__convert_into_match_day_dto(response.json())
        else:
            logger.error(
                f"Cannot get next matches. "
                f"response code: {response.status_code}, response text: {response.text}"
            )

    @staticmethod
    def __convert_into_match_day_dto(match_days: dict) -> MatchDayDTO:
        try:
            return MatchDayDTO(**match_days)
        except Exception as e:
            logger.error(e)
