import datetime

from pydantic import BaseModel

from context.enums import MatchDayStatusEnum


class MatchDaySchema(BaseModel):
    id: int
    match_date: datetime.datetime
    opponent: str
    is_home: bool
    matchday_status: MatchDayStatusEnum
    match_type: str
