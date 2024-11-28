from enum import Enum


class MatchDayStatusEnum(Enum):
    NOTSTARTED = "notstarted"
    PASSED = "passed"
    POSTPONED = "postponed"


class UserRoleEnum(Enum):
    ADMIN = "ADMIN"
    USER = "USER"
