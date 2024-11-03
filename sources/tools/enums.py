from enum import Enum


class MatchDayStatusEnum(Enum):
    PLANNED = "PLANNED"
    PASSED = "PASSED"
    POSTPONED = "POSTPONED"


class UserRoleEnum(Enum):
    ALL = "ALL"
    ADMIN = "ADMIN"
    USER = "USER"
