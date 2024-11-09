from enum import Enum


class MatchDayStatusEnum(Enum):
    PLANNED = "PLANNED"
    PASSED = "PASSED"
    POSTPONED = "POSTPONED"


class UserRoleEnum(Enum):
    ADMIN = "ADMIN"
    USER = "USER"
