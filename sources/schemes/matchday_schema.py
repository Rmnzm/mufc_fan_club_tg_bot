import datetime

from pydantic import BaseModel

from context.enums import MatchDayStatusEnum


class MatchDaySchema(BaseModel):
    id: int
    start_timestamp: datetime.datetime
    opponent_name: str
    opponent_name_slug: str
    match_status: MatchDayStatusEnum
    tournament_name: str
    tournament_name_slug: str
    localed_match_day_name: str
