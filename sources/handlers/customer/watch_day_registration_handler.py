import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from callback_factory.callback_factory import MatchDayCallbackFactory
from config.config import get_settings
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.main_keyboard import MainKeyboard
from keyboards.watch_day_keyboard import WatchDayKeyboard
from lexicon.BASE_LEXICON_RU import BASE_LEXICON_RU
from states.main_states import WatchDayUserRegistrationStateGroup

logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()
main_keyboard = MainKeyboard()
watch_day_keyboard = WatchDayKeyboard()

match_day_manager = KznRedsPGManager()


@router.callback_query(MatchDayCallbackFactory.filter())
async def process_scheduled_match_days_filter(
        callback: CallbackQuery, callback_data: MatchDayCallbackFactory, state: FSMContext
):
    watch_day_by_id = match_day_manager.get_watch_day_by_id(callback_data.id)

    nearest_match_day = (
        f"{watch_day_by_id[0].meeting_date.strftime('%a, %d %b %H:%M')}\n"
        f"{watch_day_by_id[0].tournament_name}\n"
        f"{watch_day_by_id[0].localed_match_day_name}\n"
        f"{watch_day_by_id[0].place_name}\n"
        f"{watch_day_by_id[0].address}\n\n"
        f"(встреча назначена за пол часа до события)"
    )

    await state.set_state(WatchDayUserRegistrationStateGroup.watch_day_id)

    await callback.message.edit_text(
        text=nearest_match_day, reply_markup=watch_day_keyboard.approve_meeting_keyboard()
    )
    await state.update_data(watch_day_id=callback_data.id)
    await callback.answer()


@router.callback_query(F.data == "go_button", WatchDayUserRegistrationStateGroup.watch_day_id)
async def process_go_button(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    print(state_data['watch_day_id'])

    user_id = callback.from_user.id
    print(user_id)
    try:
        match_day_manager.register_user_to_watch(user_id, state_data['watch_day_id'])

        await callback.message.edit_text(
            text="Вы зарегистрировались на матч", reply_markup=main_keyboard.main_keyboard()
        )
    except Exception as e:
        await callback.message.edit_text(
            text="Вы уже зарегистрировались на матч, ждем вас", reply_markup=main_keyboard.main_keyboard()
        )
    await callback.answer()


@router.callback_query(F.data == "not_go_button", WatchDayUserRegistrationStateGroup.watch_day_id)
async def process_not_go_button(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Жаль...", reply_markup=main_keyboard.main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "menu_button", WatchDayUserRegistrationStateGroup.watch_day_id)
async def process_menu_button(callback: CallbackQuery):
    await callback.message.edit_text(
        text=BASE_LEXICON_RU['/start'], reply_markup=main_keyboard.main_keyboard()
    )
    await callback.answer()