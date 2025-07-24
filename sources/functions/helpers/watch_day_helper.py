from datetime import timedelta
from functions.schema_converter import SchemaConverter
from schemes.scheme import NearestMeetingsSchema
from lexicon.calendar_lexicon_ru import MONTHS_RU, WEEKDAYS_RU
from lexicon.watch_day_lexicon_ru import WATCH_DAY_LEXICON_RU


class WatchDayHelper:
    @staticmethod
    def watch_day_by_id_context(watch_day_by_id: list[NearestMeetingsSchema]):
        date_str, time_str, gathering_str = WatchDayHelper.format_match_date(
            watch_day_by_id[0].meeting_date
        )
        nearest_match_day = WATCH_DAY_LEXICON_RU["nearest_match_day"].format(
            localed_match_day_name=watch_day_by_id[0].localed_match_day_name,
            date_str=date_str,
            time_str=time_str,
            gathering_str=gathering_str,
            place_name=watch_day_by_id[0].place_name,
            address=watch_day_by_id[0].address
        )

        watch_day_by_id_dict = [
            SchemaConverter().convert_model_to_dict(watch_day)
            for watch_day in watch_day_by_id
        ]
        for watch_day in watch_day_by_id_dict:
            watch_day["meeting_date"] = watch_day["meeting_date"].isoformat()

        return nearest_match_day, watch_day_by_id_dict
    
    @staticmethod
    def format_match_date(meeting_date, gathering_offset_hours=0.5):
        weekday = WEEKDAYS_RU[meeting_date.weekday()]
        day = meeting_date.day
        month = MONTHS_RU[meeting_date.month]
        
        formatted_date = f"{weekday}, {day} {month}"
        formatted_time = meeting_date.strftime("%H:%M")
        
        gathering_time = (meeting_date - timedelta(hours=gathering_offset_hours)).strftime("%H:%M")
        
        return formatted_date, formatted_time, gathering_time
