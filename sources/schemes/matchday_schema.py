import datetime

from pydantic import BaseModel

from tools.enums import MatchDayStatusEnum


class MatchDaySchema(BaseModel):
    id: int
    match_date: datetime.datetime
    opponent: str
    is_home: bool
    matchday_status: MatchDayStatusEnum
