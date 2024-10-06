from enum import Enum


class MatchDayStatusEnum(Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    PASSED = "PASSED"
    POSTPONED = "POSTPONED"
