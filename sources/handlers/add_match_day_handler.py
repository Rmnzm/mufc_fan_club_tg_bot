from datetime import datetime

from config.config import get_settings
from functions.match_day_manager import MatchDayManager

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar, DialogCalendarCallback, \
    get_user_locale

from lexicon.MATCH_DAY_ADDING_LEXICON_RU import MATCH_DAY_ADDING_LEXICON_RU
from states.main_states import MatchDayAddingStateGroup

settings = get_settings()

router = Router()

match_day_manager = MatchDayManager()


@router.message(MatchDayAddingStateGroup.opponent)
async def add_opponent(message: Message, state: FSMContext):
    opponent = message.text
    print(f"{opponent=}")

    await state.update_data(opponent=opponent)
    await state.set_state(MatchDayAddingStateGroup.is_home)

    await message.answer(
        text=MATCH_DAY_ADDING_LEXICON_RU["add_is_home"],
        reply_markup=await SimpleCalendar().start_calendar()
    )


# @router.callback_query(MatchDayAddingStateGroup.opponent)
# async def add_opponent(callback: CallbackQuery, state: FSMContext):
#     opponent = callback.data
#     print(f"{opponent=}")
#
#     await state.update_data(opponent=opponent)
#     await state.set_state(MatchDayAddingStateGroup.is_home)
#
#     await callback.answer()


@router.callback_query(MatchDayAddingStateGroup.is_home)
async def add_is_home(callback: CallbackQuery, state: FSMContext):
    is_home = callback.data
    await state.update_data(is_home=is_home)

    await state.set_state(MatchDayAddingStateGroup.match_type)

    await callback.answer()


@router.callback_query(MatchDayAddingStateGroup.match_type)
async def add_match_type(callback: CallbackQuery, state: FSMContext):
    match_type = callback.data

    await state.update_data(match_type=match_type)
    await state.set_state(MatchDayAddingStateGroup.match_date)

    await callback.answer()


@router.callback_query(SimpleCalendarCallback.filter())
async def add_match_date(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    print(f"Current state = {await state.get_state()}")
    if selected:
        await callback_query.message.answer(
            f'You selected {date.strftime("%d/%m/%Y")}'
        )
    await state.set_state(MatchDayAddingStateGroup.match_date)
    await callback_query.answer()
    print(f"Now state = {await state.get_state()}")
    print("Here")


@router.callback_query(MatchDayAddingStateGroup.match_date)
async def alalalalal(callback: CallbackQuery, state: FSMContext):
    match_date = callback.data
    print(f"{match_date=}")

    await state.update_data(match_date=match_date)
    await state.set_state(MatchDayAddingStateGroup.apply_match_day)

    print(await state.get_data())
    await callback.answer()
