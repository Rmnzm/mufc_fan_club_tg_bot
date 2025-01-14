import logging
from datetime import datetime, timedelta

from connector.kzn_reds_pg_connector import KznRedsPgConnector
from context.enums import UserRoleEnum
from schemes.scheme import MatchDaySchema, WatchDaySchema, NearestMeetingsSchema, UsersSchema, \
    PlacesSchema

logger = logging.getLogger(__name__)


class KznRedsPGManager:

    def __init__(self):
        self.kzn_reds_pg_connector = KznRedsPgConnector()

    def get_match_days(self):
        current_date = datetime.now()
        command = f"""SELECT * FROM public.match_day 
        WHERE match_status = 'notstarted' and start_timestamp > '{current_date}'"""
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        match_days = self.__convert_match_day_info(command_result)
        return_string = "\n".join(
            f"{match_day.start_timestamp.strftime('%a, %d %b %H:%M')}\n"
            f"{match_day.tournament_name}\n{match_day.localed_match_day_name}\n"
            for match_day in match_days
        )

        return return_string if return_string else "Нет ближайших матчей"

    def get_nearest_match_day(self):
        current_date = datetime.now()
        command = f"""
                    SELECT * FROM public.match_day 
                    WHERE match_status = 'notstarted' and start_timestamp > '{current_date}' 
                    ORDER BY start_timestamp DESC
        """
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        match_days = self.__convert_match_day_info(command_result)

        return match_days

    def get_places(self):
        command = "SELECT * FROM public.places"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)

        return self.__convert_places(command_result)

    def add_match_day(self, start_timestamp, match_status, opponent_name, opponent_name_slug, tournament_name,
                      tournament_name_slug, localed_match_day_name):
        try:
            command = f"""
                        INSERT INTO public.match_day (
                        start_timestamp, match_status, opponent_name, opponent_name_slug, 
                        tournament_name, tournament_name_slug, localed_match_day_name) 
                        VALUES ('{datetime.fromtimestamp(start_timestamp)}', '{match_status}', 
                        '{opponent_name}', '{opponent_name_slug}', '{tournament_name}', 
                        '{tournament_name_slug}', '{localed_match_day_name}')
                        ON CONFLICT ON CONSTRAINT match_day_pk DO NOTHING;
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
                        public.watch_day.meeting_date > '{current_date}'"""
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        print(command_result)
        nearest_meetings = self.__convert_nearest_meetings(command_result)
        return nearest_meetings

    def get_match_day_by_id(self, match_day_id):
        command = f"SELECT * FROM public.match_day WHERE id = {match_day_id}"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)

        match_day_by_id = self.__convert_match_day_info(command_result)

        return match_day_by_id[0]

    def get_watch_day_by_match_day_id(self, match_day_id: int) -> list[NearestMeetingsSchema]:
        command = (f"SELECT public.watch_day.id as watch_day_id, * FROM public.watch_day "
                   f"JOIN public.match_day ON public.watch_day.match_day_id = public.match_day.id "
                   f"JOIN public.places ON public.watch_day.place_id = public.places.id "
                   f"WHERE public.match_day.id = {match_day_id}")
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)

        watch_day_by_id = self.__convert_nearest_meetings(command_result)
        return watch_day_by_id

    def register_user_to_watch(self, user_id, watch_day_id, match_day_id, place_id):
        watch_day_info = self.get_watch_day_by_match_day_id(match_day_id)
        watch_day_date = watch_day_info[0].meeting_date.strftime('%d_%m_%Y')
        watch_day_table_name = f"match_day_{watch_day_date}"

        command = (f"INSERT INTO public.{watch_day_table_name} (user_id, watch_day_id, match_day_id, place_id) "
                   f"VALUES ({user_id}, {watch_day_id}, {match_day_id}, {place_id})")

        self.kzn_reds_pg_connector.execute_command(command, "added", "failed")


    def cancel_registration_to_watch(self, user_id, watch_day_id):
        watch_day_info = self.get_watch_day_by_match_day_id(watch_day_id)
        watch_day_date = watch_day_info[0].meeting_date.strftime('%d_%m_%Y')
        watch_day_table_name = f"match_day_{watch_day_date}"

        user_registration = self.get_user_watch_day_registration_info(user_id, watch_day_table_name)

        print(f"{user_registration=}")

        if user_registration:
            command = f"UPDATE {watch_day_table_name} SET is_canceled = true WHERE user_id = {user_id}"
            self.kzn_reds_pg_connector.execute_command(command, "added", "failed")


    def get_user_watch_day_registration_info(self, user_id, table_name):
        command = f"SELECT * FROM {table_name} WHERE user_id = {user_id}"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)

        print(command_result)

        return command_result


    def get_match_day_id_watch_day_id(self, watch_day_id):
        command = f"SELECT match_day_id FROM public.watch_day WHERE id = {watch_day_id}"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        print(command_result)

        return int(command_result[0]['match_day_id'])


    def get_users(self):
        command = "SELECT * FROM users"
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)

        users = self.__convert_users_info(command_result)

        return users

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
