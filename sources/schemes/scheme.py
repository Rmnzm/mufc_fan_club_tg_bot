import datetime
from typing import Optional

from pydantic import BaseModel

from enums import MatchDayStatusEnum, UserRoleEnum


class MatchDaySchema(BaseModel):
    id: int
    start_timestamp: datetime.datetime
    opponent_name: str
    opponent_name_slug: str
    match_status: MatchDayStatusEnum
    tournament_name: str
    tournament_name_slug: str
    localed_match_day_name: str
    event_id: Optional[int]


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
    watch_day_id: int
    meeting_date: datetime.datetime
    match_day_id: int
    place_id: int
    localed_match_day_name: str
    tournament_name: str
    place_name: str
    address: str


class UsersSchema(BaseModel):
    username: str | None
    user_role: str = "USER"
    first_name: str | None
    last_name: str | None


class PlacesSchema(BaseModel):
    id: int
    place_name: str
    address: str


class UserRegistrationSchema(BaseModel):
    user_id: int
    is_approved: bool
    is_canceled: bool


class InvitationContextSchema(BaseModel):
    meeting_date: datetime.datetime
    match_day_id: int
    place_id: int


class UserRegistrationTableSchema(BaseModel):
    id: int
    created_at: datetime.datetime
    user_id: int
    is_approved: bool
    is_canceled: bool
    watch_day_id: int
    match_day_id: int
    place_id: int
    is_message_sent: bool
