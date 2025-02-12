import logging
from datetime import datetime, timedelta

from connector.kzn_reds_pg_connector import KznRedsPgConnector
from context.enums import UserRoleEnum
from schemes.scheme import MatchDaySchema, WatchDaySchema, NearestMeetingsSchema, UsersSchema, \
    PlacesSchema, UserRegistrationSchema, InvitationContextSchema
from tools.helpers import CommonHelpers

logger = logging.getLogger(__name__)


class KznRedsPGManager:

    def __init__(self):
        self.kzn_reds_pg_connector = KznRedsPgConnector()

    def get_match_days(self):
        current_date = datetime.now()
        command = f"""SELECT * FROM public.match_day 
        WHERE match_status = 'notstarted' and start_timestamp > '{current_date}' ORDER BY start_timestamp ASC LIMIT 5;"""
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        match_days = self.__convert_match_day_info(command_result)
        return_string = "\n".join(
            f"{match_day.start_timestamp.strftime('%a, %d %b %H:%M')}\n"
            f"{match_day.tournament_name}\n{match_day.localed_match_day_name}\n"
            for match_day in match_days
        )

        return return_string if return_string else "Нет ближайших матчей"

    def get_match_day_by_event_id(self, event_id: int):
        try:
            command = f"""SELECT * FROM public.match_day WHERE event_id = {event_id} ORDER BY start_timestamp ASC LIMIT 5;"""
            command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
            print(command_result, type(command_result))
            if command_result:
                return self.__convert_match_day_info(command_result)
        except Exception as e:
            logger.error(e)

    def get_nearest_watching_day(self):
        try:
            command = ("SELECT meeting_date, match_day_id, place_id "
                       "FROM public.watch_day "
                       "ORDER BY meeting_date ASC "
                       "LIMIT 1")
            command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
            if command_result:
                return self.__convert_invitations_context(command_result)
        except Exception as e:
            logger.error(e)


    def get_users_by_watch_day_table(self, table_name):
        try:
            command = f"SELECT user_id FROM public.{table_name}"
            command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)

            if command_result:
                return command_result
        except Exception as e:
            logger.error(e)


    def update_passed_match_day(self, event_id, start_timestamp, match_status):
        try:
            command = f"""UPDATE public.match_day SET start_timestamp = '{start_timestamp}', match_status = '{match_status}' WHERE event_id = {event_id};"""

            self.kzn_reds_pg_connector.execute_command(command, "updated", "failed")
        except Exception as e:
            logger.error(e)

    @staticmethod
    def get_update_match_day_table_command(event_id, start_timestamp, match_status, opponent_name, opponent_name_slug, tournament_name,
                                           tournament_name_slug, localed_match_day_name):
        try:
            command = f"""UPDATE public.match_day 
            SET start_timestamp = '{datetime.fromtimestamp(start_timestamp)}', 
            match_status = '{match_status}', 
            opponent_name = '{opponent_name}', 
            opponent_name_slug = '{opponent_name_slug}', 
            tournament_name = '{tournament_name}', 
            tournament_name_slug = '{tournament_name_slug}', 
            localed_match_day_name = '{localed_match_day_name}'
            WHERE event_id = {event_id};"""

            return command

        except Exception as e:
            logger.error(e)

    @staticmethod
    def rename_watch_day_table_name(old_name, new_name):
        try:
            command = f"""ALTER TABLE {old_name}
                            RENAME TO {new_name};"""

            return command
        except Exception as e:
            logger.error(e)


    def update_match_day_info(self, command):
        try:
            self.kzn_reds_pg_connector.execute_command(command, "updated", "failed")
        except Exception as e:
            logger.error(e)

    @staticmethod
    def get_update_meeting_date_command(new_date, match_id):
        try:
            command = f"""UPDATE public.watch_day SET meeting_date = '{new_date}' WHERE match_day_id = {match_id};"""

            return command
        except Exception as e:
            logger.error(e)

    def get_nearest_match_day(self):
        current_date = datetime.now()
        command = f"""
                    SELECT * FROM public.match_day 
                    WHERE match_status = 'notstarted' and start_timestamp > '{current_date}' 
                    ORDER BY start_timestamp ASC LIMIT 5;
        """
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        match_days = self.__convert_match_day_info(command_result)

        return match_days

    def get_places(self):
        command = "SELECT * FROM public.places"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)

        return self.__convert_places(command_result)

    def get_place_by_id(self, place_id: int):
        command = f"SELECT * FROM public.places WHERE id = {place_id}"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)

        return self.__convert_places(command_result)

    def add_match_day(self, start_timestamp, match_status, opponent_name, opponent_name_slug, tournament_name,
                      tournament_name_slug, localed_match_day_name, event_id):
        try:
            command = f"""
                        INSERT INTO public.match_day (
                        start_timestamp, match_status, opponent_name, opponent_name_slug, 
                        tournament_name, tournament_name_slug, localed_match_day_name, event_id) 
                        VALUES ('{datetime.fromtimestamp(start_timestamp)}', '{match_status}', 
                        '{opponent_name}', '{opponent_name_slug}', '{tournament_name}', 
                        '{tournament_name_slug}', '{localed_match_day_name}', {event_id})
                        ON CONFLICT (event_id) DO UPDATE SET 
                        start_timestamp = '{datetime.fromtimestamp(start_timestamp)}',
                        match_status = '{match_status}';
                        """
            self.kzn_reds_pg_connector.execute_command(command, "added", "failed")
        except Exception as e:
            logger.error(e)

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
                        )
                        VALUES ('{match_day_context.start_timestamp - timedelta(minutes=30)}', 
                                {match_day_context.id},
                                {place_id})
                        ON CONFLICT ON CONSTRAINT match_day_id_unique DO NOTHING;
            """
            self.kzn_reds_pg_connector.execute_command(command, "added", "failed")
        except Exception as e:
            logger.error(e)

    def create_watch_day_table(self, match_day_context: MatchDaySchema):
        try:
            table_name = f"match_day_{match_day_context.start_timestamp.strftime('%d_%m_%Y')}"
            command = f"""
                        CREATE TABLE
                          public.{table_name} (
                            id serial NOT NULL,
                            created_at timestamp without time zone NOT NULL DEFAULT now(),
                            user_id integer NOT NULL REFERENCES users (user_tg_id),
                            is_approved boolean NOT NULL DEFAULT false,
                            is_canceled boolean NOT NULL DEFAULT false,
                            watch_day_id integer NOT NULL REFERENCES watch_day (id),
                            match_day_id integer NOT NULL REFERENCES match_day (id),
                            place_id integer NOT NULL REFERENCES places (id)
                          );
                        
                        ALTER TABLE
                          public.{table_name}
                        ADD
                          CONSTRAINT {table_name}_pkey PRIMARY KEY (id);
                        
            """
            self.kzn_reds_pg_connector.execute_command(command, "added", "failed")
            print(f"Table {table_name} successfully created")

            command = f"CREATE UNIQUE INDEX {table_name}_user_id_unique ON public.{table_name}(user_id);"
            self.kzn_reds_pg_connector.execute_command(command, "index created", "failed")
            print(f"Created unique index on table {table_name}")
        except Exception as e:
            logger.error(e)


    def get_nearest_watch_day(self):
        current_date = datetime.now()
        command = f"""SELECT * FROM public.watch_day 
                WHERE watch_status = 'notstarted' and meeting_date > '{current_date}'"""
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        watch_days = self.__convert_watch_day_info(command_result)

        return watch_days

    def get_nearest_meetings(self):
        current_date = datetime.now()
        command = f"""SELECT public.watch_day.id as watch_day_id, * FROM public.watch_day 
                        JOIN public.match_day ON public.watch_day.match_day_id = public.match_day.id
                        JOIN public.places ON public.watch_day.place_id = public.places.id 
                        WHERE public.watch_day.watch_status = 'notstarted' and 
                        public.match_day.match_status = 'notstarted' and 
                        public.watch_day.meeting_date > '{current_date}'
                        LIMIT 5;"""
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        print(command_result)
        nearest_meetings = self.__convert_nearest_meetings(command_result)
        return nearest_meetings

    def get_watch_day_by_match_day_id(self, match_day_id: int) -> list[NearestMeetingsSchema]:
        command = (f"SELECT public.watch_day.id as watch_day_id, * FROM public.watch_day "
                   f"JOIN public.match_day ON public.watch_day.match_day_id = public.match_day.id "
                   f"JOIN public.places ON public.watch_day.place_id = public.places.id "
                   f"WHERE public.match_day.id = {match_day_id}")
        print(f"{match_day_id=}\n{command=}")
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)

        watch_day_by_id = self.__convert_nearest_meetings(command_result)
        return watch_day_by_id

    def register_user_to_watch(self, user_id, watch_day_id, match_day_id, place_id):
        watch_day_table_name = self.__get_watch_day_table_name(match_day_id=match_day_id)

        command = (f"INSERT INTO public.{watch_day_table_name} (user_id, watch_day_id, match_day_id, place_id) "
                   f"VALUES ({user_id}, {watch_day_id}, {match_day_id}, {place_id})")

        self.kzn_reds_pg_connector.execute_command(command, "added", "failed")


    def finish_registration(self, user_id: int, match_day_id, is_approved: bool = True, is_canceled: bool = False):
        watch_day_table_name = self.__get_watch_day_table_name(match_day_id=match_day_id)
        user_registration = self.__get_user_watch_day_registration_info(
            user_id=user_id, table_name=watch_day_table_name
        )
        print(f"{watch_day_table_name=}")
        print(f"{user_registration=}")

        if user_registration:
            if is_canceled:
                command = f"UPDATE public.{watch_day_table_name} SET is_canceled = {is_canceled} WHERE user_id = {user_id}"
            else:
                command = (f"UPDATE public.{watch_day_table_name} "
                           f"SET is_approved = {is_approved}, is_canceled = {is_canceled} "
                           f"WHERE user_id = {user_id}")

            self.kzn_reds_pg_connector.execute_command(
                command, "registration finished", "registration failed"
            )
        else:
            logger.warning(f"Пользователь {user_id=} не зарегистрирован на событие")


    def __get_watch_day_table_name(self, match_day_id: int):
        watch_day_info = self.get_watch_day_by_match_day_id(match_day_id)
        print(f"{watch_day_info=}")
        watch_day_date = watch_day_info[0].meeting_date.strftime('%d_%m_%Y')
        watch_day_table_name = f"match_day_{watch_day_date}"

        return watch_day_table_name

    def cancel_registration_to_watch(self, user_id, watch_day_id):
        watch_day_info = self.get_watch_day_by_match_day_id(watch_day_id)
        watch_day_date = watch_day_info[0].meeting_date.strftime('%d_%m_%Y')
        watch_day_table_name = f"match_day_{watch_day_date}"

        user_registration = self.__get_user_watch_day_registration_info(user_id, watch_day_table_name)

        print(f"{user_registration=}")

        if user_registration:
            command = f"UPDATE {watch_day_table_name} SET is_canceled = true WHERE user_id = {user_id}"
            self.kzn_reds_pg_connector.execute_command(command, "added", "failed")


    def __get_user_watch_day_registration_info(self, user_id, table_name):
        command = f"SELECT * FROM {table_name} WHERE user_id = {user_id}"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)

        print(command_result)

        return command_result


    def get_match_day_id_watch_day_id(self, watch_day_id):
        command = f"SELECT match_day_id FROM public.watch_day WHERE id = {watch_day_id}"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        print(command_result)

        return int(command_result[0]['match_day_id'])

    def get_match_day_name_by_id(self, match_day_id: int):
        command = f"SELECT localed_match_day_name FROM public.match_day WHERE id = {match_day_id}"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)

        return command_result[0].get("localed_match_day_name")


    def get_users(self):
        command = "SELECT * FROM users"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)

        users = self.__convert_users_info(command_result)

        return users

    def approve_watch_day_by_user_invitation_info(self, table_name, user_id, match_day_id):
        try:
            command = f"""UPDATE public.{table_name} SET is_approved = true, is_canceled = false WHERE user_id = {user_id} and match_day_id = {match_day_id}"""

            print(command)
            self.kzn_reds_pg_connector.execute_command(command, "updated", "failed")
        except Exception as e:
            logger.error(e)

    def cancel_watch_day_by_user_invitation_info(self, table_name, user_id, match_day_id):
        try:
            command = f"""UPDATE public.{table_name} SET is_canceled = true, is_approved = false WHERE user_id = {user_id} and match_day_id = {match_day_id}"""
            print(command)
            self.kzn_reds_pg_connector.execute_command(command, "updated", "failed")
        except Exception as e:
            logger.error(e)

    def add_watch_place(self, place_name: str, place_address: str):
        try:
            command = f"INSERT INTO public.places (place_name, address) VALUES ('{place_name}', '{place_address}')"
            self.kzn_reds_pg_connector.execute_command(command, "added", "failed")
        except Exception as e:
            logger.error(e)


    def delete_place(self, place_id: int):
        try:
            command = f"DELETE FROM public.places WHERE id = {place_id}"
            self.kzn_reds_pg_connector.execute_command(command, "deleted", "failed")
        except Exception as e:
            logger.error(e)


    def change_place_name(self, place_id: int, new_place_name: str):
        try:
            new_place_name = new_place_name.replace("'", "''")
            command = f"UPDATE public.places SET place_name = '{new_place_name}' WHERE id = {place_id}"
            self.kzn_reds_pg_connector.execute_command(command, "updated", "failed")
        except Exception as e:
            logger.error(e)


    def change_place_address(self, place_id: int, new_place_address: str):
        try:
            command = f"UPDATE public.places SET address = '{new_place_address}' WHERE id = {place_id}"
            self.kzn_reds_pg_connector.execute_command(command, "updated", "failed")
        except Exception as e:
            logger.error(e)

    def change_watch_day_place(self, watch_day_id: int, place_id: int):
        try:
            command = f"UPDATE public.watch_day SET place_id = {place_id} WHERE id = {watch_day_id}"
            self.kzn_reds_pg_connector.execute_command(command, "updated", "failed")
        except Exception as e:
            logger.error(e)


    def delete_watch_day(self, watch_day_id: int, watch_day_table):
        try:
            command = f"BEGIN;DROP TABLE {watch_day_table};DELETE FROM public.watch_day WHERE id = {watch_day_id};END;"
            self.kzn_reds_pg_connector.execute_command(command, "deleted", "failed")
        except Exception as e:
            logger.error(e)

    def show_visitors(self, watch_day_table):
        try:
            command = f"SELECT u.username, u.user_role, u.first_name, u.last_name FROM public.{watch_day_table} JOIN public.users as u ON public.{watch_day_table}.user_id = u.user_tg_id"
            command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)

            converted_result = self.__convert_users_info(command_result)
            return converted_result
        except Exception as e:
            logger.error(e)


    def register_user(self, user_tg_id: int, user_schema: UsersSchema):
        try:
            if not self.__is_user_already_registered(user_tg_id=user_tg_id, user_schema=user_schema):
                command = (f"INSERT INTO public.users (user_tg_id, username, first_name, last_name, user_role) VALUES "
                           f"({user_tg_id}, "
                           f"'{user_schema.username}', "
                           f"'{user_schema.first_name}', "
                           f"'{user_schema.last_name}', "
                           f"'{user_schema.user_role}')")
                self.kzn_reds_pg_connector.execute_command(command, "created", "failed")
        except Exception as e:
            logger.error(e)


    def __is_user_already_registered(self, user_tg_id: int, user_schema: UsersSchema):
        try:
            command = f"SELECT * FROM public.users WHERE user_tg_id = {user_tg_id}"
            command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)

            print(f"{command_result=}")

            if command_result:
                command = (f"UPDATE public.users SET "
                            f"username = '{user_schema.username}', first_name = '{user_schema.first_name}', "
                           f"last_name = '{user_schema.last_name}' WHERE user_tg_id = {user_tg_id}")
                self.kzn_reds_pg_connector.execute_command(command, "updated", "failed")

            return command_result
        except Exception as e:
            logger.error(e)


    def get_users_to_send_invitations(self, match_day_id):
        match_day_info = self.get_watch_day_by_match_day_id(match_day_id=match_day_id)
        table_name = CommonHelpers.table_name_by_date(match_day_info[0].meeting_date)
        try:
            return self.__get_users_to_match_day(table_name, match_day_id)
        except Exception as e:
            logger.error(e)

    def __get_users_to_match_day(self, table_name: str, match_day_id: int):
        try:
            command = f"""SELECT user_id, is_approved, is_canceled 
                            FROM public.{table_name} 
                            WHERE is_canceled = false and match_day_id = {match_day_id}"""
            command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
            return self.__convert_users_registration(command_result)
        except Exception as e:
            logger.error(e)

    @staticmethod
    def __convert_users_info(users):
        return [UsersSchema(**user) for user in users]


    @staticmethod
    def __convert_match_day_info(match_days):
        return [MatchDaySchema(**match_day) for match_day in match_days]

    @staticmethod
    def __convert_watch_day_info(watch_days):
        return [WatchDaySchema(**watch_day) for watch_day in watch_days]

    @staticmethod
    def __convert_nearest_meetings(nearest_meetings):
        return [NearestMeetingsSchema(**nearest_meeting) for nearest_meeting in nearest_meetings]

    @staticmethod
    def __convert_places(places):
        return [PlacesSchema(**place) for place in places]

    @staticmethod
    def __convert_users_registration(users):
        return [UserRegistrationSchema(**user) for user in users]

    @staticmethod
    def __convert_invitations_context(invitations):
        return [InvitationContextSchema(**context) for context in invitations]
