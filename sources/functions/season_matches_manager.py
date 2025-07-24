import asyncio
import logging
import aiohttp
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

    async def update_next_matches(self, events: List[EventDTO]):
        if not events:
            logger.info("No matches to update")
            return

        tasks = []
        for event in events:
            task = asyncio.create_task(self._process_single_match(event))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_single_match(self, event: EventDTO):
        try:
            match_day = await match_day_manager.get_match_day_by_event_id(event.eventId)
            match_status = MatchDayStatusEnum.PASSED if event.score else MatchDayStatusEnum.NOTSTARTED
            opponent_name, opponent_name_slug = event.rival.name, event.rival.name_eng
            tournament_name = event.competition.short
            tournament_name_slug = event.competition.id
            localed_match_day_name = self.__get_localed_match_day_name(event)
            
            if not match_day:
                await match_day_manager.add_match_day(
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
                    await asyncio.gather(
                        match_day_manager.update_match_day_info(
                            event_id=event.eventId,
                            start_timestamp=event.date,
                            match_status=match_status,
                            opponent_name=opponent_name,
                            opponent_name_slug=opponent_name_slug,
                            tournament_name=tournament_name,
                            tournament_name_slug=tournament_name_slug,
                            localed_match_day_name=localed_match_day_name,
                        ),
                        match_day_manager.update_meeting_date(
                            match_id=match_day[0].id,
                            new_date=event.date - timedelta(minutes=30),
                        )
                    )
                else:
                    logger.debug(f"No changes for event {event.eventId}")
        except Exception as e:
            logger.error(f"Error processing event {event.eventId}: {e}")
            raise

    @staticmethod
    async def create_context_to_send_invitations():
        context = await match_day_manager.get_nearest_watching_day()
        if not context:
            return None, None
        logger.info(f"Send invitations current context = {context}")

        meeting_date = context[0].meeting_date.strftime("%a, %d %b %H:%M")

        users = await match_day_manager.get_users_to_send_invitations(context[0].match_day_id)
        match_day_name = await match_day_manager.get_match_day_name_by_id(
            context[0].match_day_id
        )
        place_info = await match_day_manager.get_place(context[0].place_id)

        match_day_info = {
            "match_day_id": context[0].match_day_id,
            "match_day_name": match_day_name,
            "place_name": place_info.place_name,
            "address": place_info.address,
            "meeting_date": meeting_date,
        }

        return users, match_day_info

    @staticmethod
    async def update_user_message_sent_status(context, user_id: int):
        match_day_id = context.get("match_day_id")
        await match_day_manager.update_message_sent_status(
            user_id=user_id, match_day_id=match_day_id
        )

    @staticmethod
    def __check_match_day_has_changes(
        event: EventDTO, 
        match_day_schema: MatchDaySchema
    ) -> bool:
        """Checks if critical match day data has changed.
        
        Args:
            event: Event data transfer object
            match_day_schema: Current match day schema
            
        Returns:
            bool: True if data remains unchanged, False if changes detected
        """
        return (
            event.date.timestamp() == match_day_schema.start_timestamp
            and event.eventId == match_day_schema.event_id
        )

    async def get_next_matches(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://manutd.one/restApi/getFixtures") as resp:
                status_code = resp.status
                if status_code == 200:
                    data = await resp.json()
                    return self.__convert_into_match_day_dto(data)
                else:
                    logger.error(
                        f"Cannot get next matches. "
                        f"response code: {status_code}, response text: {resp.text}"
                    )

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
