import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from callback_factory.callback_factory import AdminMatchDayCallbackFactory
from config.config import get_settings
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.admin_keyboard import AdminKeyboard
from states.main_states import WatchDayInfoStateGroup

logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()
admin_watch_day_keyboard = AdminKeyboard()

match_day_manager = KznRedsPGManager()


@router.callback_query(AdminMatchDayCallbackFactory.filter())
async def process_scheduled_match_days_filter(
        callback: CallbackQuery, callback_data: AdminMatchDayCallbackFactory, state: FSMContext
):
    watch_day_by_id = match_day_manager.get_watch_day_by_match_day_id(callback_data.id)

    nearest_match_day = (
        f"{watch_day_by_id[0].meeting_date.strftime('%a, %d %b %H:%M')}\n"
        f"{watch_day_by_id[0].tournament_name}\n"
        f"{watch_day_by_id[0].localed_match_day_name}\n"
        f"{watch_day_by_id[0].place_name}\n"
        f"{watch_day_by_id[0].address}\n\n"
        f"(встреча назначена за пол часа до события)"
    )

    # await state.set_state(WatchDayUserRegistrationStateGroup.watch_day_id)
    await state.set_state(WatchDayInfoStateGroup.watch_day_id)
    await state.update_data(watch_day_by_id=watch_day_by_id)

    await callback.message.edit_text(
        text=nearest_match_day, reply_markup=admin_watch_day_keyboard.edit_meeting_keyboard()
    )
    # await state.update_data(watch_day_id=callback_data.id)
    await callback.answer()


@router.callback_query(F.data == "edit_place")
async def process_go_button(callback: CallbackQuery, state: FSMContext):
    watch_day_state_data = await state.get_data()
    watch_day_info = watch_day_state_data['watch_day_by_id']
    # TODO: Добавить функционал
    await callback.message.edit_text(
        text="Изменено", reply_markup=admin_watch_day_keyboard.main_admin_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_meeting")
async def process_not_go_button(callback: CallbackQuery, state: FSMContext):
    watch_day_state_data = await state.get_data()
    watch_day_info = watch_day_state_data['watch_day_by_id']
    # TODO: Добавить функционал
    await callback.message.edit_text(
        text="Встреча отменена.", reply_markup=admin_watch_day_keyboard.main_admin_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "show_visitors")
async def process_show_visitors(callback: CallbackQuery, state: FSMContext):
    watch_day_state_data = await state.get_data()
    watch_day_info = watch_day_state_data['watch_day_by_id']
    watch_day_table = f'watch_day_{watch_day_info[0].meeting_date.strftime("%d_%m_%Y")}'

    print(watch_day_table)

    await callback.message.edit_text(
        text="Показаны участники встречи", reply_markup=admin_watch_day_keyboard.main_admin_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data == "back_to_main_menu")
async def process_menu_button(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Главное меню управления ботом.\n\nВыберите интересующую функцию.",
        reply_markup=admin_watch_day_keyboard.main_admin_keyboard()
    )
    await callback.answer()