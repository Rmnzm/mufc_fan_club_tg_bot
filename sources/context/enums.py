from enum import Enum


class MatchDayStatusEnum(Enum):
    NOTSTARTED = "notstarted"
    PASSED = "passed"
    POSTPONED = "postponed"
    FINISHED = "finished"


class UserRoleEnum(Enum):
    ADMIN = "ADMIN"
    USER = "USER"
