import logging

import requests

from functions.kzn_reds_pg_manager import KznRedsPGManager
from schemes.matchday_dto import MatchDayDTO, NearestEventsDTO, EventDTO
from config.config import get_settings

settings = get_settings()

logger = logging.getLogger(__name__)
match_day_manager = KznRedsPGManager()


class SeasonMatchesManager:
    def __init__(self):
        pass

    def update_next_matches(self, next_matches: MatchDayDTO):

        for num, event in enumerate(next_matches.events):
            # TODO: remove 0
            if num == 0:
                start_timestamp = event.startTimestamp
                match_status = event.status.type
                opponent_name, opponent_name_slug = self.__get_opponent_names(event)
                tournament_name = event.tournament.name
                tournament_name_slug = event.tournament.slug
                localed_match_day_name = self.__get_localed_match_day_name(event)
                match_day_manager.add_match_day(
                    start_timestamp=start_timestamp,
                    match_status=match_status,
                    opponent_name=opponent_name,
                    opponent_name_slug=opponent_name_slug,
                    tournament_name=tournament_name,
                    tournament_name_slug=tournament_name_slug,
                    localed_match_day_name=localed_match_day_name
                )


    def update_last_passed_match(self, nearest_events: NearestEventsDTO):
        pass

    def get_next_matches(self):
        response = requests.get(
            f"{settings.sofascore_rapidapi_url}/teams/get-next-matches?teamId={settings.team_id}&pageIndex=0",
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

    def get_nearest_events(self):
        response = requests.get(
            f"{settings.sofascore_rapidapi_url}/teams/get-near-events?teamId={settings.team_id}",
            headers={
                "x-rapidapi-host": settings.x_rapidapi_host,
                "x-rapidapi-key": settings.x_rapidapi_key
            }
        )
        if response.status_code == 200:
            return self.__convert_next_events_dto(response.json())
        else:
            logger.error(
                f"Cannot get next event. "
                f"response code: {response.status_code}, response text: {response.text}"
            )

    def __update_passed_event(self):
        pass

    def __update_first_nearest_event(self):
        pass

    @staticmethod
    def __convert_into_match_day_dto(match_days: dict) -> MatchDayDTO:
        try:
            return MatchDayDTO(**match_days)
        except Exception as e:
            logger.error(e)


    @staticmethod
    def __convert_next_events_dto(match_days: dict) -> NearestEventsDTO:
        try:
            return NearestEventsDTO(**match_days)
        except Exception as e:
            logger.error(e)

    @staticmethod
    def __get_opponent_names(event: EventDTO):
        if event.homeTeam.slug == "manchester-united":
            return event.awayTeam.name, event.awayTeam.slug
        else:
            return event.homeTeam.name, event.homeTeam.slug

    @staticmethod
    def __get_localed_match_day_name(event: EventDTO):
        return (
            f"{event.homeTeam.fieldTranslations.nameTranslation.ru} -- "
            f"{event.awayTeam.fieldTranslations.nameTranslation.ru}"
        )

