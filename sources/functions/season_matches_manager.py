import logging
from datetime import timedelta, datetime

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
            match_day = match_day_manager.get_match_day_by_id(event.id)
            start_timestamp = event.startTimestamp
            match_status = event.status.type
            opponent_name, opponent_name_slug = self.__get_opponent_names(event)
            tournament_name = event.tournament.name
            tournament_name_slug = event.tournament.slug
            localed_match_day_name = self.__get_localed_match_day_name(event)
            # TODO: remove 0
            if not match_day:
                if num == 0:
                    match_day_manager.add_match_day(
                        start_timestamp=start_timestamp,
                        match_status=match_status,
                        opponent_name=opponent_name,
                        opponent_name_slug=opponent_name_slug,
                        tournament_name=tournament_name,
                        tournament_name_slug=tournament_name_slug,
                        localed_match_day_name=localed_match_day_name,
                        event_id=event.id
                    )
            else:
                match_day_manager.update_match_day_by_event_id(
                    event_id=event.id,
                    start_timestamp=start_timestamp,
                    match_status=match_status,
                    opponent_name=opponent_name,
                    opponent_name_slug=opponent_name_slug,
                    tournament_name=tournament_name,
                    tournament_name_slug=tournament_name_slug,
                    localed_match_day_name=localed_match_day_name
                )
                match_day_manager.update_meeting_date(
                    match_id=match_day.id, new_date=datetime.fromtimestamp(start_timestamp) - timedelta(minutes=30)
                )
                old_date = datetime.fromtimestamp(start_timestamp).date().strftime("%d_%m_%Y")
                new_date = datetime.fromtimestamp(event.startTimestamp).date().strftime("%d_%m_%Y")
                match_day_manager.rename_watch_day_table_name(
                    old_name=f"match_day_{old_date}", new_name=f"match_day_{new_date}"
                )


    def update_last_passed_match(self, nearest_events: NearestEventsDTO):
        start_timestamp = nearest_events.nextEvent.startTimestamp
        match_status = nearest_events.nextEvent.status.type
        opponent_name, opponent_name_slug = self.__get_opponent_names(nearest_events.nextEvent)
        tournament_name = nearest_events.nextEvent.tournament.name
        tournament_name_slug = nearest_events.nextEvent.tournament.slug
        localed_match_day_name = self.__get_localed_match_day_name(nearest_events.nextEvent)
        match_day_manager.add_match_day(
            start_timestamp=start_timestamp,
            match_status=match_status,
            opponent_name=opponent_name,
            opponent_name_slug=opponent_name_slug,
            tournament_name=tournament_name,
            tournament_name_slug=tournament_name_slug,
            localed_match_day_name=localed_match_day_name,
            event_id=nearest_events.nextEvent.id
        )

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

