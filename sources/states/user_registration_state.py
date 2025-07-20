from aiogram.fsm.state import StatesGroup, State


class UserRegistrationState(StatesGroup):
    start_state = State()
    add_start_fan_state = State()
    add_birthday_date_state = State()
    add_favorite_player_state = State()
