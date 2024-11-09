import logging
from datetime import datetime

from connector.kzn_reds_pg_connector import KznRedsPgConnector
from context.enums import UserRoleEnum
from schemes.scheme import MatchDaySchema, UserRoleSchema

logger = logging.getLogger(__name__)


class MatchDayManager:

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
        return_string = (
            f"{match_days[0].start_timestamp.strftime('%a, %d %b %H:%M')}\n"
            f"{match_days[0].tournament_name}\n"
            f"{match_days[0].localed_match_day_name}"
        )

        return return_string

    def get_user_info(self, user_id):
        command = """SELECT user_role FROM public.users where user_id = %s""".format(user_id)
        command_result = self.kzn_reds_pg_connector.select_with_dict_result(command)

        return self.__convert_user_info(command_result)

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

    def add_user_info(self, user_id: int, user_name: str):
        try:
            command = f"""
                        INSERT INTO public.users (
                        username, user_tg_id, user_role
                        )
                        VALUES ('{user_name}', '{user_id}', '{UserRoleEnum.USER.value}')
                        ON CONFLICT ON CONSTRAINT username_userid_unique DO NOTHING
            """
            self.kzn_reds_pg_connector.execute_command(command, "added", "failed")
        except Exception as e:
            logger.error(e)

    @staticmethod
    def __convert_match_day_info(match_days):
        return [MatchDaySchema(**match_day) for match_day in match_days]

    @staticmethod
    def __convert_user_info(user_info):
        return UserRoleSchema(**user_info[0])
