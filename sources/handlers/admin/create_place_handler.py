import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config.config import get_settings
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.admin_keyboard import AdminKeyboard
from states.create_place_state import CreatePlaceStateGroup

logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()
match_day_manager = KznRedsPGManager()
admin_keyboard = AdminKeyboard()


@router.message(CreatePlaceStateGroup.start_state)
async def input_place_name(message: Message, state: FSMContext):
    await state.set_state(CreatePlaceStateGroup.add_place_state)
    await state.set_data(dict(add_place_state=message.text))

    await message.answer(text=f"Название добавлено: {message.text}")


@router.message(CreatePlaceStateGroup.add_place_state)
async def input_place_address(message: Message, state: FSMContext):
    current_state_data = await state.get_data()

    await state.set_data(dict(add_address_state=message.text))

    try:
        match_day_manager.add_watch_place(
            place_name=current_state_data['add_place_state'],
            place_address=message.text
        )

        await message.answer(
            text=f"Место сбора добавлено", reply_markup=admin_keyboard.main_admin_keyboard())
    except Exception as e:
        raise e
