from aiogram.fsm.state import StatesGroup, State


class CreatePlaceStateGroup(StatesGroup):
    start_state = State()
    add_address_state = State()
    add_place_state = State()
