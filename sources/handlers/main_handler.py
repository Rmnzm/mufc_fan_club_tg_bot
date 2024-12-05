import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from callback_factory.callback_factory import MatchDayCallbackFactory
from config.config import get_settings
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.keyboard_generator import KeyboardGenerator
from keyboards.main_keyboard import MainKeyboard
from lexicon.BASE_LEXICON_RU import BASE_LEXICON_RU
from schemes.matchday_dto import EventDTO

logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()
main_keyboard = MainKeyboard()

match_day_manager = KznRedsPGManager()
keyboard_generator = KeyboardGenerator()


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
    # nearest_match_day = (
    #     f"{nearest_match_day_context[0].meeting_date.strftime('%a, %d %b %H:%M')}\n"
    #     f"{nearest_match_day_context[0].tournament_name}\n"
    #     f"{nearest_match_day_context[0].localed_match_day_name}\n"
    #     f"{nearest_match_day_context[0].place_name}\n"
    #     f"{nearest_match_day_context[0].address}\n\n"
    #     f"(встреча назначена за пол часа до события)"
    # )
    await callback.message.edit_text(
        # TODO: add relevant text
        text="Some text",
        reply_markup=reply_keyboard
    )
    await callback.answer()


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
