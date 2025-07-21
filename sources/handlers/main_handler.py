import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from callback_factory.callback_factory import MatchDayCallbackFactory
from config.config import get_settings
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.keyboard_generator import KeyboardGenerator
from keyboards.main_keyboard import MainKeyboard
from keyboards.watch_day_keyboard import WatchDayKeyboard
from lexicon.base_lexicon_ru import BASE_LEXICON_RU, BASE_ERROR_LEXICON_RU
from schemes.scheme import MatchDaySchema
from lexicon.user_registration_lexicon import USER_REGISTRATION_LEXICON_RU
from states.user_registration_state import UserRegistrationState
from aiogram_calendar import DialogCalendar

logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()
main_keyboard = MainKeyboard()
watch_day_keyboard = WatchDayKeyboard()
keyboard_generator = KeyboardGenerator()

match_day_manager = KznRedsPGManager()


@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    if await match_day_manager.get_user_info(user_id):
        await match_day_manager.add_user_info(
            user_id=user_id, user_name=username, first_name=first_name, last_name=last_name
            )
        await message.answer(
            text=BASE_LEXICON_RU["/start"], reply_markup=main_keyboard.main_keyboard()
        )
    else:
        await state.set_state(UserRegistrationState.start_state)
        await state.set_data(
            dict(
                user_id=user_id, 
                username=username, 
                first_name=first_name, 
                last_name=last_name
                )
            )
        await message.answer(
            text=USER_REGISTRATION_LEXICON_RU["add_birthday_date"], 
            reply_markup=await DialogCalendar().start_calendar(2000)
            )


@router.callback_query(F.data == "scheduled_match_days")
async def process_scheduled_match_days(callback: CallbackQuery):
    try:
        nearest_matches = await match_day_manager.get_match_days()
        await callback.message.edit_text(
            text=__fetched_nearest_matches(nearest_matches),
            reply_markup=main_keyboard.main_keyboard(),
        )
    except Exception:
        await callback.message.edit_text(
            text=BASE_ERROR_LEXICON_RU["internal_error"],
            reply_markup=main_keyboard.main_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data == "nearest_meetings")
async def process_nearest_meetings(callback: CallbackQuery):
    try:
        nearest_match_day_context = await match_day_manager.get_nearest_meetings()
        data_factories = [
            MatchDayCallbackFactory(id=context.match_day_id)
            for context in nearest_match_day_context
        ]
        reply_keyboard = keyboard_generator.watch_day_keyboard(
            data_factories, nearest_match_day_context
        )
        if nearest_match_day_context:
            await callback.message.edit_text(
                text=BASE_LEXICON_RU["nearest_meetings_footer"], reply_markup=reply_keyboard
            )
        else:
            await callback.message.edit_text(
                text=BASE_LEXICON_RU["has_no_nearest_meetings"],
                reply_markup=main_keyboard.main_keyboard(),
            )
    except Exception:
        await callback.message.edit_text(
            text=BASE_ERROR_LEXICON_RU["internal_error"],
            reply_markup=main_keyboard.main_keyboard(),
        )
    await callback.answer()


def __fetched_nearest_matches(match_days: list[MatchDaySchema]):
    return_string = "\n".join(
        f"{match_day.start_timestamp.strftime('%a, %d %b %H:%M')}\n"
        f"{match_day.tournament_name}\n{match_day.localed_match_day_name}\n"
        for match_day in match_days
    )
    if return_string:
        return f"""{BASE_LEXICON_RU["scheduled_match_days_header"]}\n\n{return_string}\n\n{BASE_LEXICON_RU["scheduled_match_days_footer"]}"""
    return BASE_LEXICON_RU["has_no_nearest_meetings"]
