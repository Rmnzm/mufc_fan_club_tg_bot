from datetime import datetime

from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from config.config import get_settings
from functions.kzn_reds_pg_manager import KznRedsPGManager
from schemes.matchday_dto import EventDTO
from states.main_states import MatchDayAddingStateGroup

settings = get_settings()

router = Router()

match_day_manager = KznRedsPGManager()


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



# @router.callback_query(F.data == 'add_match_days')
# async def process_add_match_day(callback: CallbackQuery):
#     next_matches = SeasonMatchesManager().get_next_matches()
#     for num, event in enumerate(next_matches.events):
#         if num == 0:
#             start_timestamp = event.startTimestamp
#             match_status = event.status.type
#             opponent_name, opponent_name_slug = get_opponent_names(event)
#             tournament_name = event.tournament.name
#             tournament_name_slug = event.tournament.slug
#             localed_match_day_name = get_localed_match_day_name(event)
#             match_day_manager.add_match_day(
#                 start_timestamp=start_timestamp,
#                 match_status=match_status,
#                 opponent_name=opponent_name,
#                 opponent_name_slug=opponent_name_slug,
#                 tournament_name=tournament_name,
#                 tournament_name_slug=tournament_name_slug,
#                 localed_match_day_name=localed_match_day_name
#             )
#
#     # TODO: Make real text
#     await callback.message.edit_text(text="Заглушка! Текста пока нет. Но что-то произошло")
#     await callback.message.answer(text=BASE_LEXICON_RU['/start'], reply_markup=main_keyboard.main_keyboard())


def get_opponent_names(event: EventDTO):
    if event.homeTeam.slug == "manchester-united":
        return event.awayTeam.name, event.awayTeam.slug
    else:
        return event.homeTeam.name, event.homeTeam.slug


def get_localed_match_day_name(event: EventDTO):
    return (
        f"{event.homeTeam.fieldTranslations.nameTranslation.ru} -- "
        f"{event.awayTeam.fieldTranslations.nameTranslation.ru}"
    )
