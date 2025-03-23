import logging
from datetime import datetime, timedelta
from typing import List, Optional

from connector.kzn_reds_pg_connector import KznRedsPgConnector
from context.enums import UserRoleEnum
from schemes.scheme import (
    MatchDaySchema, WatchDaySchema, NearestMeetingsSchema, UsersSchema,
    PlacesSchema, UserRegistrationSchema, InvitationContextSchema
)
from tools.helpers import CommonHelpers

logger = logging.getLogger(__name__)

class KznRedsPGManager:

    def __init__(self):
        self.kzn_reds_pg_connector = KznRedsPgConnector()

    def get_match_days(self) -> list[MatchDaySchema]:
        try:
            current_date = datetime.now()
            command = f"""
            SELECT * FROM public.match_day
            WHERE match_status = 'notstarted' AND start_timestamp > '{current_date}'
            ORDER BY start_timestamp ASC LIMIT 5;
            """
            command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
            match_days = self.__convert_match_day_info(command_result)
            return match_days
        except Exception as e:
            logger.error(f"Error fetching match days")
            raise

    def get_match_day_by_event_id(self, event_id: int) -> List[MatchDaySchema]:
        try:
            command = f"""
            SELECT * FROM public.match_day WHERE event_id = {event_id}
            ORDER BY start_timestamp ASC LIMIT 5;
            """
            command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
            logger.debug(f"Step get_match_day_by_event_id. Command result: {command_result}")
            return self.__convert_match_day_info(command_result) if command_result else []
        except Exception as e:
            logger.error(f"Error fetching match day by event ID {event_id}: {e}")
            raise

    def check_is_table_exists(self, table_name: str) -> bool:
        try:
            command = f"""
            SELECT EXISTS(
                SELECT *
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = '{table_name}'
            );
            """
            command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
            return command_result[0].get("exists")
        except Exception as e:
            logger.error(f"Error checking if table {table_name} exists: {e}")
            raise

    def get_nearest_watching_day(self) -> List[InvitationContextSchema]:
        try:
            command = """
            SELECT meeting_date, match_day_id, place_id
            FROM public.watch_day
            WHERE meeting_date > CURRENT_DATE
            ORDER BY meeting_date ASC
            LIMIT 1
            """
            command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
            return self.__convert_invitations_context(command_result) if command_result else []
        except Exception as e:
            logger.error(f"Error fetching nearest watching day: {e}")
            raise

    def update_message_sent_status(self, table_name: str, user_id: int):
        try:
            command = f"UPDATE public.{table_name} SET is_message_sent = true WHERE user_id = {user_id}"
            self.kzn_reds_pg_connector.execute_command(
                command, f"message_status_updated for {user_id}", "message_status_update_failed"
            )
        except Exception as e:
            logger.error(f"Error updating message sent status for user {user_id} in table {table_name}: {e}")
            raise

    def get_users_by_watch_day_table(self, table_name: str) -> List[dict]:
        try:
            command = f"SELECT user_id FROM public.{table_name} WHERE is_message_sent = false;"
            command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
            return command_result if command_result else []
        except Exception as e:
            logger.error(f"Error fetching users by watch day table {table_name}: {e}")
            raise

    def update_passed_match_day(self, event_id: int, start_timestamp: datetime, match_status: str):
        try:
            command = f"""
            UPDATE public.match_day
            SET start_timestamp = '{start_timestamp}', match_status = '{match_status}'
            WHERE event_id = {event_id};
            """
            self.kzn_reds_pg_connector.execute_command(
                command, f"updated {start_timestamp}, {match_status}, {event_id}",  "failed"
            )
        except Exception as e:
            logger.error(f"Error updating passed match day for event ID {event_id}: {e}")
            raise

    @staticmethod
    def get_update_match_day_table_command(event_id: int, start_timestamp: datetime, match_status: str,
                                           opponent_name: str, opponent_name_slug: str, tournament_name: str,
                                           tournament_name_slug: str, localed_match_day_name: str) -> str:
        try:
            command = f"""
            UPDATE public.match_day
            SET start_timestamp = '{start_timestamp}', match_status = '{match_status}', opponent_name = '{opponent_name}',
                opponent_name_slug = '{opponent_name_slug}', tournament_name = '{tournament_name}',
                tournament_name_slug = '{tournament_name_slug}', localed_match_day_name = '{localed_match_day_name}'
            WHERE event_id = {event_id};
            """
            return command
        except Exception as e:
            logger.error(f"Error generating update match day table command: {e}")
            raise

    @staticmethod
    def rename_watch_day_table_name(old_name: str, new_name: str) -> str:
        try:
            command = f"ALTER TABLE {old_name} RENAME TO {new_name};"
            return command
        except Exception as e:
            logger.error(f"Error generating rename watch day table command: {e}")
            raise

    def update_match_day_info(self, command: str):
        try:
            logger.info(f"Update match day info {command=}")
            self.kzn_reds_pg_connector.execute_command(command, "updated", "failed")
        except Exception as e:
            logger.error(f"Error updating match day info: {e}")
            raise

    @staticmethod
    def get_update_meeting_date_command(new_date: datetime, match_id: int) -> str:
        try:
            command = f"""
            UPDATE public.watch_day
            SET meeting_date = '{new_date}'
            WHERE match_day_id = {match_id};
            """
            return command
        except Exception as e:
            logger.error(f"Error generating update meeting date command: {e}")
            raise

    def get_nearest_match_day(self) -> List[MatchDaySchema]:
        current_date = datetime.now()
        command = f"""
        SELECT * FROM public.match_day
        WHERE match_status = 'notstarted' AND start_timestamp > '{current_date}'
        ORDER BY start_timestamp ASC LIMIT 5;
        """
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        return self.__convert_match_day_info(command_result)

    def get_places(self) -> List[PlacesSchema]:
        command = "SELECT * FROM public.places"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        return self.__convert_places(command_result)

    def get_place_by_id(self, place_id: int) -> List[PlacesSchema]:
        command = f"SELECT * FROM public.places WHERE id = {place_id}"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        return self.__convert_places(command_result)

    def add_match_day(self, start_timestamp: datetime, match_status: str, opponent_name: str,
                      opponent_name_slug: str, tournament_name: str, tournament_name_slug: str,
                      localed_match_day_name: str, event_id: int):
        try:
            command = f"""
            INSERT INTO public.match_day (
                start_timestamp, match_status, opponent_name, opponent_name_slug,
                tournament_name, tournament_name_slug, localed_match_day_name, event_id
            ) VALUES ('{start_timestamp}', '{match_status}', '{opponent_name}', '{opponent_name_slug}', 
            '{tournament_name}', '{tournament_name_slug}', '{localed_match_day_name}', {event_id})
            ON CONFLICT (event_id) DO UPDATE SET
                start_timestamp = '{start_timestamp}', match_status = '{match_status}';
            """
            logger.debug(f"Step add_match_day. Adding match day {command=}")
            self.kzn_reds_pg_connector.execute_command(command, "added", "failed")
        except Exception as e:
            logger.error(f"Error adding match day: {e}")
            raise

    def add_user_info(self, user_id: int, user_name: str, first_name: str = None, last_name: str = None):
        try:
            command = "INSERT INTO public.users (username, user_tg_id, user_role"

            if first_name:
                command += ", first_name"
            if last_name:
                command += ", last_name"

            command += f") VALUES ('{user_name}', '{user_id}', '{UserRoleEnum.USER.value}'"

            if first_name:
                command += f", '{first_name}'"
            if last_name:
                command += f", '{last_name}'"

            command += ") ON CONFLICT (user_tg_id) DO UPDATE SET username = EXCLUDED.username"

            if first_name:
                command += ", first_name = EXCLUDED.first_name"
            if last_name:
                command += ", last_name = EXCLUDED.last_name"

            self.kzn_reds_pg_connector.execute_command(command, "added", "failed")
        except Exception as e:
            logger.error(e)


    def add_watch_day(self, match_day_context: MatchDaySchema, place_id: int):
        try:
            command = f"""
            INSERT INTO public.watch_day (
                meeting_date, match_day_id, place_id
            ) VALUES ('{match_day_context.start_timestamp - timedelta(minutes=30)}', 
                        {match_day_context.id},
                        {place_id})
            ON CONFLICT ON CONSTRAINT match_day_id_unique DO NOTHING;
            """
            self.kzn_reds_pg_connector.execute_command(command, (f"added "
                f"{match_day_context.start_timestamp - timedelta(minutes=30)} "
                f"{match_day_context.id} "
                f"{place_id}"
            ), "failed")
        except Exception as e:
            logger.error(f"Error adding watch day: {e}")
            raise

    def create_watch_day_table(self, match_day_context: MatchDaySchema):
        try:
            table_name = f"match_day_{match_day_context.start_timestamp.strftime('%d_%m_%Y')}"
            command = f"""
            CREATE TABLE public.{table_name} (
                id serial NOT NULL,
                created_at timestamp without time zone NOT NULL DEFAULT now(),
                user_id integer NOT NULL REFERENCES users (user_tg_id),
                is_approved boolean NOT NULL DEFAULT false,
                is_canceled boolean NOT NULL DEFAULT false,
                watch_day_id integer NOT NULL REFERENCES watch_day (id),
                match_day_id integer NOT NULL REFERENCES match_day (id),
                place_id integer NOT NULL REFERENCES places (id),
                is_message_sent boolean NOT NULL DEFAULT false,
                PRIMARY KEY (id)
            );
            CREATE UNIQUE INDEX {table_name}_user_id_unique ON public.{table_name}(user_id);
            """
            self.kzn_reds_pg_connector.execute_command(command, "added", "failed")
            logger.info(f"Table {table_name} successfully created")
        except Exception as e:
            logger.error(f"Error creating watch day table: {e}")
            raise

    def get_nearest_meetings(self) -> List[NearestMeetingsSchema]:
        current_date = datetime.now()
        command = f"""
        SELECT public.watch_day.id as watch_day_id, *
        FROM public.watch_day
        JOIN public.match_day ON public.watch_day.match_day_id = public.match_day.id
        JOIN public.places ON public.watch_day.place_id = public.places.id
        WHERE public.watch_day.watch_status = 'notstarted'
          AND public.match_day.match_status = 'notstarted'
          AND public.watch_day.meeting_date > '{current_date}'
        LIMIT 5;
        """
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        return self.__convert_nearest_meetings(command_result)

    def get_watch_day_by_match_day_id(self, match_day_id: int) -> List[NearestMeetingsSchema]:
        command = f"""
        SELECT public.watch_day.id as watch_day_id, *
        FROM public.watch_day
        JOIN public.match_day ON public.watch_day.match_day_id = public.match_day.id
        JOIN public.places ON public.watch_day.place_id = public.places.id
        WHERE public.match_day.id = {match_day_id}
        """
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        return self.__convert_nearest_meetings(command_result)

    def register_user_to_watch(self, user_id: int, watch_day_id: int, match_day_id: int, place_id: int):
        watch_day_table_name = self.__get_watch_day_table_name(match_day_id)
        command = f"""
        INSERT INTO public.{watch_day_table_name} (user_id, watch_day_id, match_day_id, place_id)
        VALUES ({user_id}, {watch_day_id}, {match_day_id}, {place_id})
        """
        self.kzn_reds_pg_connector.execute_command(
            command, f"added {user_id}, {watch_day_id}, {match_day_id}, {place_id}", "failed"
        )

    def finish_registration(self, user_id: int, match_day_id: int, is_approved: bool = True, is_canceled: bool = False):
        watch_day_table_name = self.__get_watch_day_table_name(match_day_id)
        user_registration = self.__get_user_watch_day_registration_info(user_id, watch_day_table_name)
        if user_registration:
            command = f"""
            UPDATE public.{watch_day_table_name}
            SET is_approved = '{is_approved}', is_canceled = '{is_canceled}'
            WHERE user_id = '{user_id}'
            """
            self.kzn_reds_pg_connector.execute_command(
                command,
                f"registration finished {is_approved}, {is_canceled}, {user_id}",
                "registration failed"
            )
        else:
            logger.warning(f"User {user_id} is not registered for the event")

    def __get_watch_day_table_name(self, match_day_id: int) -> str:
        watch_day_info = self.get_watch_day_by_match_day_id(match_day_id)
        watch_day_date = watch_day_info[0].meeting_date.strftime('%d_%m_%Y')
        return f"match_day_{watch_day_date}"

    def __get_user_watch_day_registration_info(self, user_id: int, table_name: str) -> List[dict]:
        command = f"SELECT * FROM {table_name} WHERE user_id = '{user_id}'"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        return command_result

    def get_match_day_id_watch_day_id(self, watch_day_id: int) -> int:
        command = f"SELECT match_day_id FROM public.watch_day WHERE id = {watch_day_id}"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        return int(command_result[0]['match_day_id'])

    def get_match_day_name_by_id(self, match_day_id: int) -> str:
        command = f"SELECT localed_match_day_name FROM public.match_day WHERE id = {match_day_id}"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        return command_result[0].get("localed_match_day_name")

    def get_users(self) -> List[UsersSchema]:
        command = "SELECT * FROM users"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        return self.__convert_users_info(command_result)

    def approve_watch_day_by_user_invitation_info(self, table_name: str, user_id: int, match_day_id: int):
        try:
            command = f"""
            UPDATE public.{table_name}
            SET is_approved = true, is_canceled = false
            WHERE user_id = {user_id} AND match_day_id = {match_day_id}
            """
            self.kzn_reds_pg_connector.execute_command(
                command, f"updated {user_id}, {match_day_id}",  "failed"
            )
        except Exception as e:
            logger.error(f"Error approving watch day for user {user_id} in table {table_name}: {e}")
            raise

    def cancel_watch_day_by_user_invitation_info(self, table_name: str, user_id: int, match_day_id: int):
        try:
            command = f"""
            UPDATE public.{table_name}
            SET is_canceled = true, is_approved = false
            WHERE user_id = {user_id} AND match_day_id = {match_day_id}
            """
            self.kzn_reds_pg_connector.execute_command(
                command, f"updated {user_id}, {match_day_id}", "failed"
            )
        #     TODO: HERE next
        except Exception as e:
            logger.error(f"Error canceling watch day for user {user_id} in table {table_name}: {e}")
            raise

    def add_watch_place(self, place_name: str, place_address: str):
        try:
            command = f"INSERT INTO public.places (place_name, address) VALUES ('{place_name}', '{place_address}')"
            self.kzn_reds_pg_connector.execute_command(command, "added", "failed")
        except Exception as e:
            logger.error(f"Error adding watch place: {e}")
            raise

    def delete_place(self, place_id: int):
        try:
            command = f"DELETE FROM public.places WHERE id = {place_id}"
            self.kzn_reds_pg_connector.execute_command(command, f"deleted {place_id=}", "failed")
        except Exception as e:
            logger.error(f"Error deleting place with ID {place_id}: {e}")
            raise

    def change_place_name(self, place_id: int, new_place_name: str):
        try:
            new_place_name = new_place_name.replace("'", "''")
            command = f"UPDATE public.places SET place_name = '{new_place_name}' WHERE id = '{place_id}'"
            self.kzn_reds_pg_connector.execute_command(
                command, f"updated place_name to {new_place_name}", "failed"
            )
        except Exception as e:
            logger.error(f"Error changing place name for place ID {place_id}: {e}")
            raise

    def change_place_address(self, place_id: int, new_place_address: str):
        try:
            command = f"UPDATE public.places SET address = '{new_place_address}' WHERE id = {place_id}"
            self.kzn_reds_pg_connector.execute_command(
                command,  f"updated address name to {new_place_address}", "failed"
            )
        except Exception as e:
            logger.error(f"Error changing place address for place ID {place_id}: {e}")
            raise

    def change_watch_day_place(self, watch_day_id: int, place_id: int):
        try:
            command = f"UPDATE public.watch_day SET place_id = {place_id} WHERE id = {watch_day_id}"
            self.kzn_reds_pg_connector.execute_command(
                command,  f"updated {watch_day_id=} on setting {place_id=}", "failed"
            )
        except Exception as e:
            logger.error(f"Error changing watch day place for watch day ID {watch_day_id}: {e}")
            raise

    def delete_watch_day(self, watch_day_id: int, watch_day_table: str):
        try:
            command = f"BEGIN;DROP TABLE {watch_day_table};DELETE FROM public.watch_day WHERE id = {watch_day_id};END;"
            self.kzn_reds_pg_connector.execute_command(
                command,  f"deleted {watch_day_table=}", "failed"
            )
        except Exception as e:
            logger.error(f"Error deleting watch day with ID {watch_day_id}: {e}")
            raise

    def show_visitors(self, watch_day_table: str) -> List[UsersSchema]:
        try:
            command = f"""
            SELECT u.username, u.user_role, u.first_name, u.last_name
            FROM public.{watch_day_table}
            JOIN public.users as u ON public.{watch_day_table}.user_id = u.user_tg_id
            """
            command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
            return self.__convert_users_info(command_result)
        except Exception as e:
            logger.error(f"Error fetching visitors for watch day table {watch_day_table}: {e}")
            raise

    def register_user(self, user_tg_id: int, user_schema: UsersSchema):
        try:
            if not self.__is_user_already_registered(user_tg_id, user_schema):
                command = f"""
                INSERT INTO public.users (user_tg_id, username, first_name, last_name, user_role)
                VALUES (
                        {user_tg_id}, 
                        '{user_schema.username}', 
                        '{user_schema.first_name}', 
                        '{user_schema.last_name}', 
                        '{user_schema.user_role}'
                        )
                """
                self.kzn_reds_pg_connector.execute_command(
                    command, f"created user row on {user_tg_id=} with {user_schema.user_role=}", "failed"
                )
        except Exception as e:
            logger.error(f"Error registering user with TG ID {user_tg_id}: {e}")
            raise

    def __is_user_already_registered(self, user_tg_id: int, user_schema: UsersSchema) -> bool:
        try:
            command = f"SELECT * FROM public.users WHERE user_tg_id = {user_tg_id}"
            command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
            if command_result:
                command = f"""
                UPDATE public.users
                SET username = '{user_schema.username}', first_name = '{user_schema.first_name}', last_name = '{user_schema.last_name}'
                WHERE user_tg_id = {user_tg_id}
                """
                self.kzn_reds_pg_connector.execute_command(command, (
                    f"updated {user_schema.username}, {user_schema.first_name}, "
                    f"{user_schema.last_name}, {user_tg_id=}"
                ), "failed")
            return bool(command_result)
        except Exception as e:
            logger.error(f"Error checking if user with TG ID {user_tg_id} is already registered: {e}")
            raise

    def get_users_to_send_invitations(self, match_day_id: int) -> List[UserRegistrationSchema]:
        match_day_info = self.get_watch_day_by_match_day_id(match_day_id)
        table_name = CommonHelpers.table_name_by_date(match_day_info[0].meeting_date)
        return self.__get_users_to_match_day(table_name, match_day_id)

    def __get_users_to_match_day(self, table_name: str, match_day_id: int) -> List[UserRegistrationSchema]:
        try:
            command = f"""
            SELECT user_id, is_approved, is_canceled
            FROM public.{table_name}
            WHERE is_canceled = false AND match_day_id = {match_day_id}
            """
            command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
            return self.__convert_users_registration(command_result)
        except Exception as e:
            logger.error(f"Error fetching users to match day {match_day_id} in table {table_name}: {e}")
            raise

    @staticmethod
    def __convert_users_info(users: List[dict]) -> List[UsersSchema]:
        return [UsersSchema(**user) for user in users]

    @staticmethod
    def __convert_match_day_info(match_days: List[dict]) -> List[MatchDaySchema]:
        return [MatchDaySchema(**match_day) for match_day in match_days]

    @staticmethod
    def __convert_watch_day_info(watch_days: List[dict]) -> List[WatchDaySchema]:
        return [WatchDaySchema(**watch_day) for watch_day in watch_days]

    @staticmethod
    def __convert_nearest_meetings(nearest_meetings: List[dict]) -> List[NearestMeetingsSchema]:
        return [NearestMeetingsSchema(**nearest_meeting) for nearest_meeting in nearest_meetings]

    @staticmethod
    def __convert_places(places: List[dict]) -> List[PlacesSchema]:
        return [PlacesSchema(**place) for place in places]

    @staticmethod
    def __convert_users_registration(users: List[dict]) -> List[UserRegistrationSchema]:
        return [UserRegistrationSchema(**user) for user in users]

    @staticmethod
    def __convert_invitations_context(invitations: List[dict]) -> List[InvitationContextSchema]:
        return [InvitationContextSchema(**context) for context in invitations]
