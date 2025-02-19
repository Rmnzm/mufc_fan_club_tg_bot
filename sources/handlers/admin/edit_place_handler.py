import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from callback_factory.callback_factory import PlacesEditorFactory
from functions.admin_checker import admin_required, AdminFilter
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.admin_keyboard import AdminKeyboard
from keyboards.keyboard_generator import KeyboardGenerator

logger = logging.getLogger(__name__)

router = Router()

match_day_manager = KznRedsPGManager()

admin_keyboard = AdminKeyboard()
keyboard_generator = KeyboardGenerator()


class PlaceState(StatesGroup):
    place_id = State()
    delete_place = State()
    edit_name = State()
    edit_address = State()
    approve_changes = State()


@router.callback_query(PlacesEditorFactory.filter(), AdminFilter())
async def edit_place_process(
    callback: CallbackQuery, callback_data: PlacesEditorFactory, state: FSMContext
):
    place_id = callback_data.id
    await state.set_state(PlaceState.place_id)
    await state.update_data(place_id=place_id)

    await callback.message.edit_text(
        text="Выберите действие с выбранным местом",
        reply_markup=admin_keyboard.edit_place_keyboard(name=True, address=True)
    )
    await callback.answer()

@router.callback_query(F.data == "edit_name", AdminFilter())
async def edit_place_name_process(
    callback: CallbackQuery, state: FSMContext
):
    await state.set_state(PlaceState.edit_name)
    await callback.message.answer(
        text="Введите название места"
    )
    await callback.answer()


@router.message(PlaceState.edit_name, AdminFilter())
async def edit_place_name(message: Message, state: FSMContext):
    place_state_data = await state.get_data()
    place_id = place_state_data['place_id']
    new_place_name = message.text

    try:
        match_day_manager.change_place_name(
            place_id=place_id,
            new_place_name=new_place_name
        )
        await message.answer(
            text=f"Изменено место по {place_id=}", reply_markup=admin_keyboard.edit_place_keyboard(address=True)
        )
        await state.clear()
    except Exception:
        await message.answer(
            text="Не удалось изменить название места",
            reply_markup=admin_keyboard.main_admin_keyboard()
        )

@router.callback_query(F.data == "edit_address", AdminFilter())
async def edit_address_place_process(
    callback: CallbackQuery, state: FSMContext
):
    await state.set_state(PlaceState.edit_address)
    await callback.message.answer(
        text="Введите адрес места"
    )
    await callback.answer()

@router.message(PlaceState.edit_address, AdminFilter())
async def edit_place_address(message: Message, state: FSMContext):
    place_state_data = await state.get_data()
    place_id = place_state_data['place_id']
    new_place_address = message.text

    try:
        match_day_manager.change_place_address(
            place_id=place_id,
            new_place_address=new_place_address
        )
        await message.answer(
            text=f"Изменен адрес по {place_id=}",
            reply_markup=admin_keyboard.edit_place_keyboard(name=True)
        )
    except Exception:
        await message.answer(
            text="Не удалось изменить адрес",
            reply_markup=admin_keyboard.main_admin_keyboard()
        )


@router.callback_query(F.data == "delete_place", AdminFilter())
async def delete_place(callback: CallbackQuery, state: FSMContext):
    place_state_data = await state.get_data()
    place_id = place_state_data['place_id']

    try:
        match_day_manager.delete_place(place_id=place_id)
        await callback.message.answer(
            text=f"Место удалено {place_id=}",
            reply_markup=admin_keyboard.main_admin_keyboard()
        )

        await state.clear()
    except Exception:
        await callback.message.answer(
            text="Не удалось удалить место",
            reply_markup=admin_keyboard.main_admin_keyboard()
        )
    await callback.answer()

