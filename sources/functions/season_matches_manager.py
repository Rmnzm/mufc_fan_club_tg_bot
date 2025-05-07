import logging
from datetime import timedelta, datetime

import requests

from functions.kzn_reds_pg_manager import KznRedsPGManager
from schemes.matchday_dto import MatchDayDTO, NearestEventsDTO, EventDTO
from config.config import get_settings
from schemes.scheme import MatchDaySchema, InvitationContextSchema
from tools.helpers import CommonHelpers

settings = get_settings()

logger = logging.getLogger(__name__)
match_day_manager = KznRedsPGManager()


class SeasonMatchesManager:

    def update_next_matches(self, next_matches: MatchDayDTO):
        logger.info(f"Received {len(next_matches.events)} matches to create or update")
        for num, event in enumerate(next_matches.events):
            match_day = match_day_manager.get_match_day_by_event_id(event.id)
            start_timestamp = event.startTimestamp
            match_status = event.status.type
            opponent_name, opponent_name_slug = self.__get_opponent_names(event)
            tournament_name = event.tournament.name
            tournament_name_slug = event.tournament.slug
            localed_match_day_name = self.__get_localed_match_day_name(event)
            if not match_day:
                match_day_manager.add_match_day(
                    start_timestamp=datetime.fromtimestamp(start_timestamp),
                    match_status=match_status,
                    opponent_name=opponent_name,
                    opponent_name_slug=opponent_name_slug,
                    tournament_name=tournament_name,
                    tournament_name_slug=tournament_name_slug,
                    localed_match_day_name=localed_match_day_name,
                    event_id=event.id,
                )
            else:
                if not self.__check_match_day_has_changes(event, match_day[0]):
                    update_match_day_table_command = (
                        match_day_manager.get_update_match_day_table_command(
                            event_id=event.id,
                            start_timestamp=datetime.fromtimestamp(start_timestamp),
                            match_status=match_status,
                            opponent_name=opponent_name,
                            opponent_name_slug=opponent_name_slug,
                            tournament_name=tournament_name,
                            tournament_name_slug=tournament_name_slug,
                            localed_match_day_name=localed_match_day_name,
                        )
                    )
                    update_meeting_date_command = (
                        match_day_manager.get_update_meeting_date_command(
                            match_id=match_day[0].id,
                            new_date=datetime.fromtimestamp(start_timestamp)
                            - timedelta(minutes=30),
                        )
                    )
                    old_date = match_day[0].start_timestamp.strftime("%d_%m_%Y")
                    new_date = (
                        datetime.fromtimestamp(event.startTimestamp)
                        .date()
                        .strftime("%d_%m_%Y")
                    )
                    rename_watch_day_table_command = (
                        match_day_manager.rename_watch_day_table_name(
                            old_name=f"match_day_{old_date}",
                            new_name=f"match_day_{new_date}",
                        )
                        if match_day_manager.check_is_table_exists(
                            f"match_day_{old_date}"
                        )
                        else ""
                    )

                    fully_command = (
                        update_match_day_table_command
                        + update_meeting_date_command
                        + rename_watch_day_table_command
                    )

                    match_day_manager.update_match_day_info(command=fully_command)
                else:
                    logger.info("Events has no changes")

    @staticmethod
    def create_context_to_send_invitations() -> (
        list[dict],
        list[InvitationContextSchema],
    ):
        context = match_day_manager.get_nearest_watching_day()
        logger.info(f"Send invitations current context = {context}")
        table_name = CommonHelpers.table_name_by_date(context[0].meeting_date)

        meeting_date = context[0].meeting_date.strftime("%a, %d %b %H:%M")

        users = match_day_manager.get_users_by_watch_day_table(table_name=table_name)
        match_day_name = match_day_manager.get_match_day_name_by_id(
            context[0].match_day_id
        )
        place_info = match_day_manager.get_place_by_id(context[0].place_id)

        match_day_info = {
            "match_day_id": context[0].match_day_id,
            "table_name": table_name,
            "match_day_name": match_day_name,
            "place_name": place_info[0].place_name,
            "address": place_info[0].address,
            "meeting_date": meeting_date,
        }

        return users, match_day_info

    @staticmethod
    def update_message_sent_status(context, user_id: int):
        table_name = context.get("table_name")
        match_day_manager.update_message_sent_status(
            table_name=table_name, user_id=user_id
        )

    @staticmethod
    def __check_match_day_has_changes(
        event: EventDTO, match_day_schema: MatchDaySchema
    ) -> bool:
        try:
            # TODO: add more checks
            assert (
                datetime.fromtimestamp(event.startTimestamp)
                == match_day_schema.start_timestamp
            )
            assert event.id == match_day_schema.event_id
            return True
        except AssertionError:
            return False

    def update_last_passed_match(self, nearest_events: NearestEventsDTO):
        start_timestamp = datetime.fromtimestamp(
            nearest_events.previousEvent.startTimestamp
        )
        match_status = nearest_events.previousEvent.status.type
        localed_match_day_name = self.__get_localed_match_day_name(
            nearest_events.previousEvent
        )
        match_day_manager.update_passed_match_day(
            start_timestamp=start_timestamp,
            match_status=match_status,
            event_id=nearest_events.previousEvent.id,
        )

        logger.info(
            f"Updated passed on {start_timestamp.date().strftime('%d_%m_%Y')} match day "
            f"{localed_match_day_name} with changing status to {match_status}"
        )

    def get_next_matches(self):
        response = requests.get(
            f"{settings.sofascore_rapidapi_url}/teams/get-next-matches?teamId={settings.sofascore_team_id}&pageIndex=0",
            headers={
                "x-rapidapi-host": settings.x_rapidapi_host,
                "x-rapidapi-key": settings.x_rapidapi_key,
            },
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
            f"{settings.sofascore_rapidapi_url}/teams/get-near-events?teamId={settings.sofascore_team_id}",
            headers={
                "x-rapidapi-host": settings.x_rapidapi_host,
                "x-rapidapi-key": settings.x_rapidapi_key,
            },
        )
        if response.status_code == 200:
            return self.__convert_next_events_dto(response.json())
        else:
            logger.error(
                f"Cannot get next event. "
                f"response code: {response.status_code}, response text: {response.text}"
            )

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
