from aiogram.fsm.state import StatesGroup, State


class MatchDayAddingStateGroup(StatesGroup):
    opponent = State()
    is_home = State()
    match_date = State()
    match_type = State()
    apply_match_day = State()


class WatchDayUserRegistrationStateGroup(StatesGroup):
    watch_day_id = State()
    user_id = State()
