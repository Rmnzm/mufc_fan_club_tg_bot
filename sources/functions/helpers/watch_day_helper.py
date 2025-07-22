from datetime import timedelta
from functions.schema_converter import SchemaConverter
from schemes.scheme import NearestMeetingsSchema
from lexicon.calendar_lexicon_ru import MONTHS_RU, WEEKDAYS_RU


class WatchDayHelper:
    @staticmethod
    def watch_day_by_id_context(watch_day_by_id: list[NearestMeetingsSchema]):
        # TODO: переписать под макроподстановки и базовое сообщение
        # nearest_match_day = (
        #     f"{watch_day_by_id[0].meeting_date.strftime('%a, %d %b %H:%M')}\n"
        #     f"{watch_day_by_id[0].tournament_name}\n"
        #     f"{watch_day_by_id[0].localed_match_day_name}\n"
        #     f"{watch_day_by_id[0].place_name}\n"
        #     f"{watch_day_by_id[0].address}\n\n"
        #     f"(встреча назначена за пол часа до события)"
        # )

        date_str, time_str, gathering_str = WatchDayHelper.__format_match_date(
            watch_day_by_id[0].meeting_date
        )
        nearest_match_day = (
            f"🔴 Фан-встреча\n "
            f"{watch_day_by_id[0].localed_match_day_name}\n\n"
            f"📅 {date_str} \n"
            f"⏰ {time_str} (сбор с {gathering_str})\n\n"
            f"🏟️ {watch_day_by_id[0].place_name}\n"
            f"📍 {watch_day_by_id[0].address}"
        )

        watch_day_by_id_dict = [
            SchemaConverter().convert_model_to_dict(watch_day)
            for watch_day in watch_day_by_id
        ]
        for watch_day in watch_day_by_id_dict:
            watch_day["meeting_date"] = watch_day["meeting_date"].isoformat()

        return nearest_match_day, watch_day_by_id_dict
    
    def __format_match_date(meeting_date, gathering_offset_hours=0.5):
        weekday = WEEKDAYS_RU[meeting_date.weekday()]
        day = meeting_date.day
        month = MONTHS_RU[meeting_date.month]
        
        formatted_date = f"{weekday}, {day} {month}"
        formatted_time = meeting_date.strftime("%H:%M")
        
        # Рассчитываем время сбора
        gathering_time = (meeting_date - timedelta(hours=gathering_offset_hours)).strftime("%H:%M")
        
        return formatted_date, formatted_time, gathering_time
