import logging
from datetime import timedelta, datetime
from typing import List

import requests

from functions.kzn_reds_pg_manager import KznRedsPGManager
from schemes.matchday_dto import EventDTO
from config.config import get_settings
from schemes.scheme import MatchDaySchema, InvitationContextSchema
from enums import EventPlaceEnum, MatchDayStatusEnum
from tools.helpers import CommonHelpers

settings = get_settings()

logger = logging.getLogger(__name__)
match_day_manager = KznRedsPGManager()


class SeasonMatchesManager:

    def update_next_matches(self, events: List[EventDTO]):
        if not events:
            logger.info("No matches to update")
            return

        logger.info(f"Received {len(events)} matches to create or update")
        for event in events:
            match_day = match_day_manager.get_match_day_by_event_id(event.eventId)
            match_status = MatchDayStatusEnum.PASSED if event.score else MatchDayStatusEnum.NOTSTARTED
            opponent_name, opponent_name_slug = event.rival.name, event.rival.name_eng
            tournament_name = event.competition.short
            tournament_name_slug = event.competition.id
            localed_match_day_name = self.__get_localed_match_day_name(event)
            if not match_day:
                match_day_manager.add_match_day(
                    start_timestamp=event.date,
                    match_status=match_status,
                    opponent_name=opponent_name,
                    opponent_name_slug=opponent_name_slug,
                    tournament_name=tournament_name,
                    tournament_name_slug=tournament_name_slug,
                    localed_match_day_name=localed_match_day_name,
                    event_id=event.eventId,
                )
            else:
                if not self.__check_match_day_has_changes(event, match_day[0]):
                    update_match_day_table_command = (
                        match_day_manager.get_update_match_day_table_command(
                            event_id=event.eventId,
                            start_timestamp=event.date,
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
                            new_date=event.date - timedelta(minutes=30),
                        )
                    )

                    fully_command = (
                        update_match_day_table_command
                        + update_meeting_date_command
                    )

                    match_day_manager.update_match_day_info(command=fully_command)
                else:
                    logger.info("Events has no changes")

    @staticmethod
    def create_context_to_send_invitations():
        context = match_day_manager.get_nearest_watching_day()
        if not context:
            return None, None
        logger.info(f"Send invitations current context = {context}")

        meeting_date = context[0].meeting_date.strftime("%a, %d %b %H:%M")

        users = match_day_manager.get_users_to_send_invitations(context[0].match_day_id)
        match_day_name = match_day_manager.get_match_day_name_by_id(
            context[0].match_day_id
        )
        place_info = match_day_manager.get_place_by_id(context[0].place_id)

        match_day_info = {
            "match_day_id": context[0].match_day_id,
            "match_day_name": match_day_name,
            "place_name": place_info[0].place_name,
            "address": place_info[0].address,
            "meeting_date": meeting_date,
        }

        return users, match_day_info

    @staticmethod
    def update_message_sent_status(context, user_id: int):
        match_day_id = context.get("match_day_id")
        match_day_manager.update_message_sent_status(
            user_id=user_id, match_day_id=match_day_id
        )

    @staticmethod
    def __check_match_day_has_changes(
        event: EventDTO, match_day_schema: MatchDaySchema
    ) -> bool:
        try:
            # TODO: add more checks and remove asserts
            logger.info("Check match day date has changes ...")
            assert event.date.timestamp() == match_day_schema.start_timestamp
            logger.info("Check match day event id has changes ...")
            assert event.id == match_day_schema.event_id
            return True
        except AssertionError:
            return False

    # def update_last_passed_match(self, nearest_events: NearestEventsDTO):
    #     if not nearest_events or not nearest_events.previousEvent:
    #         logger.info("No previous event to update")
    #         return

    #     start_timestamp = datetime.fromtimestamp(
    #         nearest_events.previousEvent.startTimestamp
    #     )
    #     match_status = nearest_events.previousEvent.status.type
    #     localed_match_day_name = self.__get_localed_match_day_name(nearest_events.previousEvent)
    #     match_day_manager.update_passed_match_day(
    #         start_timestamp=start_timestamp,
    #         match_status=match_status,
    #         event_id=nearest_events.previousEvent.id,
    #     )

    #     logger.info(
    #         f"Updated passed on {start_timestamp.date().strftime('%d_%m_%Y')} match day "
    #         f"{localed_match_day_name} with changing status to {match_status}"
    #     )

    def get_next_matches(self):
        response = requests.get("https://manutd.one/restApi/getFixtures")
        if response.status_code == 200:
            return self.__convert_into_match_day_dto(response.json())
        else:
            logger.error(
                f"Cannot get next matches. "
                f"response code: {response.status_code}, response text: {response.text}"
            )

    # def get_nearest_events(self):
    #     response = requests.get(
    #         f"{settings.sofascore_rapidapi_url}/teams/get-near-events?teamId={settings.sofascore_team_id}",
    #         headers={
    #             "x-rapidapi-host": settings.x_rapidapi_host,
    #             "x-rapidapi-key": settings.x_rapidapi_key,
    #         },
    #     )
    #     if response.status_code == 200:
    #         return self.__convert_next_events_dto(response.json())
    #     else:
    #         logger.error(
    #             f"Cannot get next event. "
    #             f"response code: {response.status_code}, response text: {response.text}"
    #         )

    @staticmethod
    def __convert_into_match_day_dto(match_days: list) -> List[EventDTO]:
        try:
            events = []
            for match_day in match_days:
                events.append(
                    EventDTO(**match_day)
                )
            return events
        except Exception as e:
            logger.error(e)

    @staticmethod
    def __get_localed_match_day_name(event: EventDTO):
        match event.place:
            case EventPlaceEnum.HOME.value:
                return f"{settings.base_team_located_ru_name} -- {event.rival.name}"
            case EventPlaceEnum.AWAY.value:
                return f"{event.rival.name} -- {settings.base_team_located_ru_name}"
