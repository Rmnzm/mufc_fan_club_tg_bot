import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from callback_factory.callback_factory import MatchDayCallbackFactory
from config.config import get_settings
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.keyboard_generator import KeyboardGenerator
from keyboards.main_keyboard import MainKeyboard
from keyboards.watch_day_keyboard import WatchDayKeyboard
from lexicon.BASE_LEXICON_RU import BASE_LEXICON_RU
from schemes.matchday_dto import EventDTO

logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()
main_keyboard = MainKeyboard()
watch_day_keyboard = WatchDayKeyboard()
keyboard_generator = KeyboardGenerator()

match_day_manager = KznRedsPGManager()


@router.message(CommandStart())
async def process_start_command(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    match_day_manager.add_user_info(user_id=user_id, user_name=username)
    await message.answer(text=BASE_LEXICON_RU['/start'], reply_markup=main_keyboard.main_keyboard())


@router.callback_query(F.data == "scheduled_match_days")
async def process_scheduled_match_days(callback: CallbackQuery):
    nearest_matches = match_day_manager.get_match_days()
    await callback.message.edit_text(text=nearest_matches, reply_markup=main_keyboard.main_keyboard())
    # TODO: replace keyboard to back_to_menu
    await callback.answer()


@router.callback_query(F.data == "nearest_meetings")
async def process_nearest_meetings(callback: CallbackQuery):
    nearest_match_day_context = match_day_manager.get_nearest_meetings()
    data_factories = [
        MatchDayCallbackFactory(
            id=context.id
        ) for context in nearest_match_day_context
    ]
    reply_keyboard = keyboard_generator.watch_day_keyboard(data_factories, nearest_match_day_context)
    await callback.message.edit_text(
        # TODO: add relevant text
        text="Some text",
        reply_markup=reply_keyboard
    )
    await callback.answer()
