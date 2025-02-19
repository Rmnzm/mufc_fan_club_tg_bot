from datetime import datetime


class CommonHelpers:

    @staticmethod
    def table_name_by_date(date: datetime):
        date_str = date.strftime("%d_%m_%Y")
        return f"match_day_{date_str}"