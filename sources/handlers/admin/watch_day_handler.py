import logging
from pyexpat.errors import messages

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from config.config import get_settings
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.main_keyboard import MainKeyboard
from keyboards.watch_day_keyboard import WatchDayKeyboard
from lexicon.BASE_LEXICON_RU import BASE_LEXICON_RU
from lexicon.WATCH_DAY_LEXICON_RU import WATCH_DAY_LEXICON_RU

logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()

match_day_manager = KznRedsPGManager()

watch_day_keyboard = WatchDayKeyboard().watch_day_keyboard()
main_keyboard = MainKeyboard().main_keyboard()


class WatchDay(StatesGroup):
    choose_match_day = State()
    edit_place_name = State()
    edit_address = State()


@router.callback_query(F.data == "nearest_match_day")
async def watch_day_handler(callback: CallbackQuery, state: FSMContext):
    nearest_match_day_context = match_day_manager.get_nearest_match_day()
    nearest_match_day = (
        f"{nearest_match_day_context[0].start_timestamp.strftime('%a, %d %b %H:%M')}\n"
        f"{nearest_match_day_context[0].tournament_name}\n"
        f"{nearest_match_day_context[0].localed_match_day_name}\n\n"
        f"(встреча будет назначена за пол часа до события)"
    )

    await callback.message.edit_text(
        text=f"{WATCH_DAY_LEXICON_RU['next_match_day_is']}\n\n{nearest_match_day}",
        reply_markup=watch_day_keyboard
    )
    await state.set_state(WatchDay.choose_match_day)
    await state.update_data(choose_match_day=nearest_match_day_context)
    await callback.answer()


@router.callback_query(F.data == "add_watch_day")
async def watch_day_register(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WatchDay.edit_place_name)

    await callback.message.edit_text(
        text=f"{WATCH_DAY_LEXICON_RU['edit_place_name']}"
    )
    await callback.answer()


@router.message(WatchDay.edit_place_name)
async def edit_place_name_handler(message: Message, state: FSMContext):
    place_name = message.text
    await state.update_data(place_name=place_name)
    await state.set_state(WatchDay.edit_address)

    await message.answer(
        text=f"{WATCH_DAY_LEXICON_RU['edit_address']}"
    )


@router.message(WatchDay.edit_address)
async def edit_address(message: Message, state: FSMContext):
    print(await state.get_data())
    # Example of state.get_data() -- {'choose_match_day': [MatchDaySchema(id=5, start_timestamp=datetime.datetime(2024, 11, 28, 23, 0), opponent_name='Bodø/Glimt', opponent_name_slug='bodoglimt', match_status=<MatchDayStatusEnum.NOTSTARTED: 'notstarted'>, tournament_name='UEFA Europa League', tournament_name_slug='uefa-europa-league', localed_match_day_name='Манчестер Юнайтед -- ФК Буде/Глимт')], 'place_name': 'top hop'}
    # TODO: register watching place. Make row with place if not exists.
    #  Add watch day and  attach link place row into watch day table
    address = message.text
    match_day_context = await state.get_data()
    match_day_manager.add_watch_day(address=address, match_day_context=match_day_context['choose_match_day'][0])
    match_day_manager.create_watch_day_table(match_day_context=match_day_context['choose_match_day'][0])

    await message.answer(
        text=f"{WATCH_DAY_LEXICON_RU['register_success']}", reply_markup=main_keyboard
    )


@router.callback_query(F.data == "cancel_adding")
async def cancel_adding_watch_day(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_text(
        text="Отменено", reply_markup=watch_day_keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "choose_another_match_day")
async def choose_another_match_day(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text="Кнопка пока не работает", reply_markup=watch_day_keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def choose_another_match_day(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text=BASE_LEXICON_RU['/start'], reply_markup=main_keyboard
    )
    await callback.answer()
