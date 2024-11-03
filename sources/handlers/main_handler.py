import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config.config import get_settings
from functions.match_day_manager import MatchDayManager
from keyboards.main_keyboard import MainKeyboard
from lexicon.BASE_LEXICON_RU import BASE_LEXICON_RU
from lexicon.MATCH_DAY_ADDING_LEXICON_RU import MATCH_DAY_ADDING_LEXICON_RU
from states.main_states import MatchDayAddingStateGroup
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar, DialogCalendarCallback, \
    get_user_locale

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


@router.callback_query(F.data == 'add_match_day')
async def process_add_match_day(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Выберем дату",
        reply_markup=await SimpleCalendar().start_calendar()
    )
    await state.set_state(MatchDayAddingStateGroup.match_date)

    print(await state.get_state())
    await callback.answer()


@router.callback_query(MatchDayAddingStateGroup.apply_match_day)
async def process_apply_match_day(callback: CallbackQuery, state: FSMContext):
    context_data = await state.get_data()
    await callback.answer()
