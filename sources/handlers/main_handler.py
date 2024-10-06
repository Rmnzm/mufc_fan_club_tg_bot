import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config.config import get_settings
from functions.match_day_manager import MatchDayManager
from keyboards.main_keyboard import MainKeyboard
from lexicon.BASE_LEXICON_RU import BASE_LEXICON_RU

settings = get_settings()

router = Router()
main_keyboard = MainKeyboard()

match_day_manager = MatchDayManager()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=BASE_LEXICON_RU['/start'], reply_markup=main_keyboard.main_keyboard())


@router.callback_query(F.data == "scheduled_match_days")
async def process_scheduled_match_days(callback: CallbackQuery):
    nearest_matches = match_day_manager.get_match_days()
    await callback.message.edit_text(text=nearest_matches)
    await callback.answer()
