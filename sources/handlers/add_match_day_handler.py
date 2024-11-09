from datetime import datetime

from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from config.config import get_settings
from functions.match_day_manager import MatchDayManager
from states.main_states import MatchDayAddingStateGroup

settings = get_settings()

router = Router()

match_day_manager = MatchDayManager()


@router.callback_query(SimpleCalendarCallback.filter())
async def add_match_date(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'You selected {date.strftime("%d/%m/%Y")}'
        )
    await state.set_state(MatchDayAddingStateGroup.match_date)
    await callback_query.answer()
