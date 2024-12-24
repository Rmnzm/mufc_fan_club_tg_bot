import logging
from tkinter import Place

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from callback_factory.callback_factory import AdminMatchDayCallbackFactory, PlacesFactory, PlacesEditorFactory
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.admin_keyboard import AdminKeyboard
from keyboards.keyboard_generator import KeyboardGenerator
from states.create_place_state import CreatePlaceStateGroup

logger = logging.getLogger(__name__)

router = Router()

match_day_manager = KznRedsPGManager()

admin_keyboard = AdminKeyboard()
keyboard_generator = KeyboardGenerator()


class PlaceState(StatesGroup):
    place_id = State()
    edit_name = State()
    edit_address = State()


@router.callback_query(PlacesEditorFactory.filter())
async def edit_place_process(
    callback: CallbackQuery, callback_data: PlacesEditorFactory, state: FSMContext
):
    place_id = callback_data.id
    await state.set_state(PlaceState.edit_name)
    await state.update_data(place_id=place_id)

    await callback.message.edit_text(
        text="Выберите действие с выбранным местом", reply_markup=admin_keyboard.edit_place_keyboard()
    )
    await callback.answer()



@router.callback_query(PlaceState.edit_name)
async def edit_place_name_process(
    callback: CallbackQuery, state: FSMContext
):
    pass


@router.callback_query(PlaceState.edit_address)
async def edit_place_address_process(
    callback: CallbackQuery, state: FSMContext
):
    pass
