import datetime
from typing import Optional

from pydantic import BaseModel

from context.enums import MatchDayStatusEnum
from context.enums import UserRoleEnum


class MatchDaySchema(BaseModel):
    id: int
    start_timestamp: datetime.datetime
    opponent_name: str
    opponent_name_slug: str
    match_status: MatchDayStatusEnum
    tournament_name: str
    tournament_name_slug: str
    localed_match_day_name: str


class UserRoleSchema(BaseModel):
    user_id: int
    username: str
    user_role: UserRoleEnum


class WatchDaySchema(BaseModel):
    id: int
    address: str
    meeting_date: datetime.datetime
    description: Optional[str]
    match_day_id: int
    place_name: str
    watch_status: MatchDayStatusEnum


class NearestMeetingsSchema(BaseModel):
    id: int
    address: str
    place_name: str
    meeting_date: datetime.datetime
    localed_match_day_name: str
    tournament_name: str


class UsersSchema(BaseModel):
    username: str
    user_role: str
