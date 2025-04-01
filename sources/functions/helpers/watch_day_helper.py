from functions.schema_converter import SchemaConverter
from schemes.scheme import NearestMeetingsSchema


class WatchDayHelper:
    @staticmethod
    def watch_day_by_id_context(watch_day_by_id: list[NearestMeetingsSchema]):
        # TODO: переписать под макроподстановки и базовое сообщение
        nearest_match_day = (
            f"{watch_day_by_id[0].meeting_date.strftime('%a, %d %b %H:%M')}\n"
            f"{watch_day_by_id[0].tournament_name}\n"
            f"{watch_day_by_id[0].localed_match_day_name}\n"
            f"{watch_day_by_id[0].place_name}\n"
            f"{watch_day_by_id[0].address}\n\n"
            f"(встреча назначена за пол часа до события)"
        )

        watch_day_by_id_dict = [
            SchemaConverter().convert_model_to_dict(watch_day) for watch_day in watch_day_by_id
        ]
        for watch_day in watch_day_by_id_dict:
            watch_day['meeting_date'] = watch_day['meeting_date'].isoformat()

        return nearest_match_day, watch_day_by_id_dict