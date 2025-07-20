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
from sources.lexicon.user_registration_lexicon import USER_REGISTRATION_ERROR_LEXICON_RU, USER_REGISTRATION_LEXICON_RU
from sources.states.user_registration_state import UserRegistrationState
from aiogram_calendar import DialogCalendarCallback, DialogCalendar, get_user_locale
from aiogram.filters.callback_data import CallbackData


logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()
main_keyboard = MainKeyboard()
watch_day_keyboard = WatchDayKeyboard()
keyboard_generator = KeyboardGenerator()

match_day_manager = KznRedsPGManager()

@router.callback_query(DialogCalendarCallback.filter())
async def process_user_birthday_date(
    callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext
    ):
    selected, date = await DialogCalendar(
        locale=await get_user_locale(callback_query.from_user)
    ).process_selection(callback_query, callback_data)
    if selected:    
        await state.set_state(UserRegistrationState.add_start_fan_state)
        await state.update_data(birthday_date=date)

        await callback_query.message.answer(f'You selected {date.strftime("%d/%m/%Y")} {USER_REGISTRATION_LEXICON_RU["add_fan_start_date"]}')

@router.message(UserRegistrationState.add_start_fan_state)
async def process_user_start_fan_date(message: Message, state: FSMContext):
    try:
        await state.set_state(UserRegistrationState.add_favorite_player_state)
        await state.update_data(start_fan_date=message.text)
        await message.answer(
            text=USER_REGISTRATION_LEXICON_RU["add_favorite_player"]
        )
    except Exception:
        await message.answer(
            text=USER_REGISTRATION_ERROR_LEXICON_RU["internal_error"],
            reply_markup=main_keyboard.main_keyboard(),
        )


@router.message(UserRegistrationState.add_favorite_player_state)
async def process_user_start_fan_date(message: Message, state: FSMContext):
    try:   
        user_data = await state.get_data()
        user_id = user_data["user_id"]
        username = user_data["username"]
        first_name = user_data["first_name"]
        last_name = user_data["last_name"]
        favorite_player = message.text
        birthday_date = user_data["birthday_date"]
        start_fan_date = user_data["start_fan_date"]
        await match_day_manager.add_user_info(
            user_id=user_id, 
            user_name=username, 
            first_name=first_name, 
            last_name=last_name,
            birthday=birthday_date,
            favorite_player=favorite_player,
            start_fan=start_fan_date
            )
        await message.answer(
            text=USER_REGISTRATION_LEXICON_RU["finish_registration"],
            reply_markup=main_keyboard.main_keyboard(),
        )
    except Exception:
        await message.answer(
            text=USER_REGISTRATION_ERROR_LEXICON_RU["internal_error"],
            reply_markup=main_keyboard.main_keyboard(),
        )

