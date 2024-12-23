import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery

from callback_factory.callback_factory import AdminCreateWatchDayCallbackFactory, \
    PlacesFactory
from config.config import get_settings
from functions.kzn_reds_pg_manager import KznRedsPGManager
from handlers.admin.base_admin_handler import admin_keyboard
from keyboards.admin_keyboard import AdminKeyboard
from keyboards.keyboard_generator import KeyboardGenerator
from keyboards.watch_day_keyboard import WatchDayKeyboard

logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()

match_day_manager = KznRedsPGManager()

watch_day_keyboard = WatchDayKeyboard().watch_day_keyboard()
main_keyboard = AdminKeyboard()
keyboard_generator = KeyboardGenerator()


class WatchDay(StatesGroup):
    choose_match_day = State()
    choose_place = State()


@router.callback_query(F.data == "add_watch_day")
async def watch_day_register(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WatchDay.choose_match_day)
    nearest_matches = match_day_manager.get_nearest_match_day()

    data_factories = [
        AdminCreateWatchDayCallbackFactory(
            id=context.id
        ) for context in nearest_matches
    ]
    reply_keyboard = keyboard_generator.admin_create_watch_day_keyboard(
        data_factories, nearest_matches, add_watch_day=False
    )

    await callback.message.edit_text(
        text=f"Выберите матч", reply_markup=reply_keyboard
    )
    await callback.answer()


@router.callback_query(AdminCreateWatchDayCallbackFactory.filter())
async def choose_place(
    callback: CallbackQuery, callback_data: AdminCreateWatchDayCallbackFactory, state: FSMContext
):
    match_day_by_id = match_day_manager.get_match_day_by_id(callback_data.id)
    await state.set_state(WatchDay.choose_place)
    await state.update_data(match_day_by_id=match_day_by_id)

    places = match_day_manager.get_places()

    data_factories = [
        PlacesFactory(id=context.id) for context in places
    ]
    reply_keyboard = keyboard_generator.places_keyboard(
        data_factories, places
    )
    await callback.message.edit_text(
        text=f"Выберите место просмотра", reply_markup=reply_keyboard
    )
    await callback.answer()


@router.callback_query(PlacesFactory.filter(), WatchDay.choose_place)
async def registrate_meeting(
        callback: CallbackQuery, callback_data: PlacesFactory, state: FSMContext
):
    current_state_data = await state.get_data()
    place_id = callback_data.id

    try:
        match_day_manager.add_watch_day(current_state_data['match_day_by_id'], place_id)
        match_day_manager.create_watch_day_table(current_state_data['match_day_by_id'])
        await callback.message.edit_text(
            text=f"Встреча добавлена", reply_markup=admin_keyboard.main_admin_keyboard()
        )
        await callback.answer()

    except Exception as e:
        raise e


