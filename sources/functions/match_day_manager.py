import json

from connector.kzn_reds_pg_connector import KznRedsPgConnector
from schemes.matchday_schema import MatchDaySchema


class MatchDayManager:

    def __init__(self):
        self.kzn_reds_pg_connector = KznRedsPgConnector()

    def get_match_days(self):
        command = """SELECT * FROM public.match_day"""
        result = self.kzn_reds_pg_connector.select_with_dict_result(command)
        match_days = self.__match_day(result)
        return_string = "\n".join(f"{match_day.match_date.isoformat()}\n{match_day.opponent}" for match_day in match_days)

        return return_string

    @staticmethod
    def __match_day(match_days):
        return [MatchDaySchema(**match_day) for match_day in match_days]
