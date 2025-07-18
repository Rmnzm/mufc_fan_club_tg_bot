import logging
from datetime import datetime, timedelta
from typing import List, Optional

from peewee import fn
from database.models.models import MatchDay, User, WatchDay, Place, UserRegistration
from database.models.base_model import objects
from enums import MatchDayStatusEnum, UserRoleEnum
from schemes.scheme import (
    MatchDaySchema,
    NearestMeetingsSchema,
    UsersSchema,
    InvitationContextSchema,
    PlacesSchema,
    UserRegistrationSchema,
)
from functions.schema_converter import SchemaConverter

logger = logging.getLogger(__name__)

class KznRedsPGManager:
    _schema_converter = SchemaConverter()

    async def get_match_days(self) -> List[MatchDaySchema]:
        try:
            current_date = datetime.now()
            query = (MatchDay
                    .select()
                    .where(
                        (MatchDay.match_status == 'notstarted') &
                        (MatchDay.start_timestamp > current_date)
                    )
                    .order_by(MatchDay.start_timestamp)
                    .limit(5))
            
            match_days = await objects.execute(query)
            return self._schema_converter.convert_match_day_info(
                [model.__data__ for model in match_days]
            )
        except Exception as e:
            logger.error("Error fetching match days", exc_info=True)
            raise

    async def get_match_day_by_event_id(self, event_id: str) -> List[MatchDaySchema]:
        try:
            query = (MatchDay
                     .select()
                     .where(MatchDay.event_id == event_id)
                     .order_by(MatchDay.start_timestamp)
                     .limit(5))
            
            match_days = await objects.execute(query)
            return (
                self._schema_converter.convert_match_day_info(
                    [model.__data__ for model in match_days]
                ) if match_days else []
            )
        except Exception as e:
            logger.error(f"Error fetching match day by event ID {event_id}", exc_info=True)
            raise

    async def get_nearest_watching_day(self) -> List[InvitationContextSchema]:
        try:
            query = (WatchDay
                     .select(WatchDay.meeting_date, WatchDay.match_day_id, WatchDay.place_id)
                     .where(WatchDay.meeting_date > datetime.now())
                     .order_by(WatchDay.meeting_date)
                     .limit(1))
            
            watch_days = await objects.execute(query)
            return (
                self._schema_converter.convert_invitations_context(
                    [model.__data__ for model in watch_days]
                ) if watch_days else []
            )
        except Exception as e:
            logger.error("Error fetching nearest watching day", exc_info=True)
            raise

    async def update_message_sent_status(self, user_id: int, match_day_id: int):        
        try:
            await objects.execute(
                UserRegistration
                .update(is_message_sent=True)
                .where(
                    (UserRegistration.user_id == user_id) &
                    (UserRegistration.match_day_id == match_day_id)
                )
            )
        except Exception as e:
            logger.error(f"Error updating message status for user {user_id}", exc_info=True)
            raise

    async def update_match_day_info(
        self,
        event_id: str,
        start_timestamp: datetime,
        match_status: MatchDayStatusEnum,
        opponent_name: str,
        opponent_name_slug: str,
        tournament_name: str,
        tournament_name_slug: str,
        localed_match_day_name: str,
    ):
        try:
            await objects.execute(
                MatchDay
                .update(
                    start_timestamp=start_timestamp,
                    match_status=match_status.value,
                    opponent_name=opponent_name,
                    opponent_name_slug=opponent_name_slug,
                    tournament_name=tournament_name,
                    tournament_name_slug=tournament_name_slug,
                    localed_match_day_name=localed_match_day_name
                )
                .where(MatchDay.event_id == event_id)
            )
        except Exception as e:
            logger.error("Error updating match day info", exc_info=True)
            raise

    async def update_meeting_date(self, new_date: datetime, match_id: int):
        try:
            await objects.execute(
                WatchDay
                .update(meeting_date=new_date)
                .where(WatchDay.match_day_id == match_id)
            )
        except Exception as e:
            logger.error(f"Error updating meeting date for match {match_id}", exc_info=True)
            raise

    async def get_nearest_match_day(self) -> List[MatchDaySchema]:
        try:
            subquery = WatchDay.select(WatchDay.match_day_id)
            query = (MatchDay
                     .select()
                     .where(
                         (MatchDay.match_status == 'notstarted') &
                         (MatchDay.start_timestamp > fn.now()) &
                         ~(MatchDay.id.in_(subquery))
                     )
                     .order_by(MatchDay.start_timestamp)
                     .limit(5))
            
            match_days = await objects.execute(query)
            return self._schema_converter.convert_match_day_info(
                [model.__data__ for model in match_days]
            )
        except Exception as e:
            logger.error("Error fetching nearest match days", exc_info=True)
            raise

    async def get_places(self) -> List[PlacesSchema]:
        try:
            query = Place.select()
            places = await objects.execute(query)
            return self._schema_converter.convert_places(
                [model.__data__ for model in places]
            )
        except Exception as e:
            logger.error("Error fetching places", exc_info=True)
            raise

    async def get_place_by_id(self, place_id: int) -> List[PlacesSchema]:
        try:
            query = Place.select().where(Place.id == place_id)
            places = await objects.execute(query)
            return self._schema_converter.convert_places(
                [model.__data__ for model in places]
            )
        except Exception as e:
            logger.error(f"Error fetching place with ID {place_id}", exc_info=True)
            raise

    async def add_match_day(
        self,
        start_timestamp: datetime,
        match_status: MatchDayStatusEnum,
        opponent_name: str,
        opponent_name_slug: str,
        tournament_name: str,
        tournament_name_slug: str,
        localed_match_day_name: str,
        event_id: str,
    ):
        try:
            await objects.create(
                MatchDay,
                start_timestamp=start_timestamp,
                match_status=match_status.value,
                opponent_name=opponent_name,
                opponent_name_slug=opponent_name_slug,
                tournament_name=tournament_name,
                tournament_name_slug=tournament_name_slug,
                localed_match_day_name=localed_match_day_name,
                event_id=event_id,
                on_conflict='update'
            )
        except Exception as e:
            logger.error("Error adding match day", exc_info=True)
            raise

    async def add_user_info(
        self,
        user_id: int,
        user_name: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ):
        try:
            try:
                user = await objects.get(User, user_tg_id=user_id)
                
                update_fields = {'username': user_name}
                if first_name:
                    update_fields['first_name'] = first_name
                if last_name:
                    update_fields['last_name'] = last_name
                    
                for field, value in update_fields.items():
                    setattr(user, field, value)
                    
                await objects.update(user)
                
            except User.DoesNotExist:
                await objects.create(
                    User,
                    user_tg_id=user_id,
                    username=user_name,
                    user_role=UserRoleEnum.USER.value,
                    first_name=first_name,
                    last_name=last_name
                )
                
        except Exception as e:
            logger.error(f"Error in add_user_info: {str(e)}", exc_info=True)
            raise

    async def add_watch_day(self, match_day_context: MatchDaySchema, place_id: int):
        try:
            await objects.create(
                WatchDay,
                meeting_date=match_day_context.start_timestamp - timedelta(minutes=30),
                match_day_id=match_day_context.id,
                place_id=place_id,
                watch_status='notstarted',
                on_conflict='ignore'
            )
        except Exception as e:
            logger.error("Error adding watch day", exc_info=True)
            raise

    async def get_nearest_meetings(self) -> List[NearestMeetingsSchema]:
        try:
            query = (
                WatchDay
                    .select(
                        WatchDay.id.alias('watch_day_id'),
                        WatchDay.meeting_date,
                        WatchDay.watch_status,
                        MatchDay.id.alias('match_day_id'),
                        MatchDay.start_timestamp,
                        MatchDay.opponent_name,
                        MatchDay.tournament_name,
                        MatchDay.localed_match_day_name,
                        Place.id.alias('place_id'),
                        Place.place_name,
                        Place.address
                    )
                    .join(MatchDay, on=(WatchDay.match_day_id == MatchDay.id))
                    .join(Place, on=(WatchDay.place_id == Place.id))
                    .where(
                        (WatchDay.watch_status == 'notstarted') &
                        (MatchDay.match_status == 'notstarted') &
                        (WatchDay.meeting_date > datetime.now())
                    )
                    .limit(5)
                )
            
            meetings = await objects.execute(query.dicts())
            
            return self._schema_converter.convert_nearest_meetings(list(meetings))
            
        except Exception as e:
            logger.error(f"Error in get_nearest_meetings: {str(e)}", exc_info=True)
            raise

    async def get_watch_day_by_match_day_id(
        self, match_day_id: int
    ) -> List[NearestMeetingsSchema]:
        try:
            query = (WatchDay
                     .select(
                        WatchDay.id.alias('watch_day_id'),
                        WatchDay.meeting_date,
                        WatchDay.watch_status,
                        MatchDay.id.alias('match_day_id'),
                        MatchDay.start_timestamp,
                        MatchDay.opponent_name,
                        MatchDay.tournament_name,
                        MatchDay.localed_match_day_name,
                        Place.id.alias('place_id'),
                        Place.place_name,
                        Place.address
                    )
                     .join(MatchDay, on=(WatchDay.match_day_id == MatchDay.id))
                     .join(Place, on=(WatchDay.place_id == Place.id))
                     .where(MatchDay.id == match_day_id))
            
            meetings = await objects.execute(query.dicts())
            return self._schema_converter.convert_nearest_meetings(list(meetings))
        
        except Exception as e:
            logger.error(f"Error fetching watch day for match {match_day_id}", exc_info=True)
            raise

    async def register_user_to_watch(
        self, user_id: int, watch_day_id: int, match_day_id: int, place_id: int
    ):
        try:
            await objects.create(
                UserRegistration,
                user_id=user_id,
                watch_day_id=watch_day_id,
                match_day_id=match_day_id,
                place_id=place_id,
                is_approved=False,
                is_canceled=False,
                is_message_sent=False,
                on_conflict={
                    'update': {
                        'watch_day_id': watch_day_id,
                        'place_id': place_id,
                        'is_approved': False,
                        'is_canceled': False,
                        'is_message_sent': False
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error registering user {user_id} for match {match_day_id}", exc_info=True)
            raise

    async def get_match_day_id_watch_day_id(self, watch_day_id: int) -> int:
        try:
            watch_day = await objects.get(WatchDay.select(WatchDay.match_day_id).where(WatchDay.id == watch_day_id))
            return watch_day.match_day_id
        except Exception as e:
            logger.error(f"Error getting match day ID for watch day {watch_day_id}", exc_info=True)
            raise

    async def get_match_day_name_by_id(self, match_day_id: int) -> str:
        try:
            match_day = await objects.get(MatchDay.select(MatchDay.localed_match_day_name).where(MatchDay.id == match_day_id))
            return match_day.localed_match_day_name
        except Exception as e:
            logger.error(f"Error getting match day name for ID {match_day_id}", exc_info=True)
            raise

    async def get_users(self) -> List[UsersSchema]:
        try:
            query = User.select()
            users = await objects.execute(query)
            return self._schema_converter.convert_users_info(
                [model.__data__ for model in users]
            )
        except Exception as e:
            logger.error("Error fetching users", exc_info=True)
            raise

    async def approve_watch_day_by_user_invitation_info(self, user_id: int, match_day_id: int):
        try:
            await objects.execute(
                UserRegistration
                .update(
                    is_approved=True,
                    is_canceled=False
                )
                .where(
                    (UserRegistration.user_id == user_id) &
                    (UserRegistration.match_day_id == match_day_id)
                )
            )
        except Exception as e:
            logger.error(f"Error approving registration for user {user_id}", exc_info=True)
            raise

    async def cancel_watch_day_by_user_invitation_info(self, user_id: int, match_day_id: int):
        try:
            await objects.execute(
                UserRegistration
                .update(
                    is_canceled=True,
                    is_approved=False
                )
                .where(
                    (UserRegistration.user_id == user_id) &
                    (UserRegistration.match_day_id == match_day_id)
                )
            )
        except Exception as e:
            logger.error(f"Error canceling registration for user {user_id}", exc_info=True)
            raise

    async def add_watch_place(self, place_name: str, place_address: str):
        try:
            await objects.create(Place, place_name=place_name, address=place_address)
        except Exception as e:
            logger.error("Error adding watch place", exc_info=True)
            raise

    async def delete_place(self, place_id: int):
        try:
            await objects.execute(Place.delete().where(Place.id == place_id))
        except Exception as e:
            logger.error(f"Error deleting place with ID {place_id}", exc_info=True)
            raise

    async def change_place_name(self, place_id: int, new_place_name: str):
        try:
            await objects.execute(
                Place
                .update(place_name=new_place_name)
                .where(Place.id == place_id)
            )
        except Exception as e:
            logger.error(f"Error changing place name for place ID {place_id}", exc_info=True)
            raise

    async def change_place_address(self, place_id: int, new_place_address: str):
        try:
            await objects.execute(
                Place
                .update(address=new_place_address)
                .where(Place.id == place_id)
            )
        except Exception as e:
            logger.error(f"Error changing place address for place ID {place_id}", exc_info=True)
            raise

    async def change_watch_day_place(self, watch_day_id: int, place_id: int):
        try:
            await objects.execute(
                WatchDay
                .update(place_id=place_id)
                .where(WatchDay.id == watch_day_id)
            )
        except Exception as e:
            logger.error(f"Error changing watch day place for watch day ID {watch_day_id}", exc_info=True)
            raise

    async def show_visitors(self, match_day_id: int) -> List[UsersSchema]:
        try:
            query = (User
                     .select()
                     .join(UserRegistration, on=(User.user_tg_id == UserRegistration.user_id))
                     .where(
                         (UserRegistration.match_day_id == match_day_id) &
                         (UserRegistration.is_canceled == False))
                     )
            
            users = await objects.execute(query)
            return self._schema_converter.convert_users_info(
                [model.__data__ for model in users]
            )
        except Exception as e:
            logger.error(f"Error fetching visitors for match {match_day_id}", exc_info=True)
            raise

    async def register_user(self, user_tg_id: int, user_schema: UsersSchema):
        try:
            exists = await objects.count(
                User.select().where(User.user_tg_id == user_tg_id)
            )
            
            if exists:
                await objects.execute(
                    User
                    .update(
                        username=user_schema.username,
                        first_name=user_schema.first_name,
                        last_name=user_schema.last_name
                    )
                    .where(User.user_tg_id == user_tg_id)
                )
            else:
                await objects.create(
                    User,
                    user_tg_id=user_tg_id,
                    username=user_schema.username,
                    first_name=user_schema.first_name,
                    last_name=user_schema.last_name,
                    user_role=user_schema.user_role
                )
        except Exception as e:
            logger.error(f"Error registering user with TG ID {user_tg_id}", exc_info=True)
            raise

    async def get_users_to_send_invitations(self, match_day_id: int) -> List[UserRegistrationSchema]:
        try:
            query = (UserRegistration
                     .select()
                     .where(
                         (UserRegistration.is_canceled == False) &
                         (UserRegistration.match_day_id == match_day_id) &
                         (UserRegistration.is_message_sent == False))
                     )
            
            registrations = await objects.execute(query)
            return self._schema_converter.convert_users_registration(
                [model.__data__ for model in registrations]
            )
        except Exception as e:
            logger.error(f"Error fetching users for match {match_day_id}", exc_info=True)
            raise
