import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, Poll, PollAnswer, PollOption
from aiogram.types import CallbackQuery

from callback_factory.callback_factory import AdminMatchDayCallbackFactory, PlacesEditorFactory, WatchPlaceChangeFactory
from config.config import get_settings
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.admin_keyboard import AdminKeyboard
from keyboards.keyboard_generator import KeyboardGenerator
from states.main_states import WatchDayInfoStateGroup

logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()
admin_watch_day_keyboard = AdminKeyboard()
places_keyboard = KeyboardGenerator()

match_day_manager = KznRedsPGManager()

class PlaceState(StatesGroup):
    watch_day_id = State()
    delete_watch_day = State()
    edit_watch_place = State()


@router.callback_query(AdminMatchDayCallbackFactory.filter())
async def process_scheduled_match_days_filter(
        callback: CallbackQuery, callback_data: AdminMatchDayCallbackFactory, state: FSMContext
):
    watch_day_by_id = match_day_manager.get_watch_day_by_match_day_id(callback_data.id)

    nearest_match_day = (
        f"{watch_day_by_id[0].meeting_date.strftime('%a, %d %b %H:%M')}\n"
        f"{watch_day_by_id[0].tournament_name}\n"
        f"{watch_day_by_id[0].localed_match_day_name}\n"
        f"{watch_day_by_id[0].place_name}\n"
        f"{watch_day_by_id[0].address}\n\n"
        f"(встреча назначена за пол часа до события)"
    )

    # await state.set_state(WatchDayUserRegistrationStateGroup.watch_day_id)
    await state.set_state(WatchDayInfoStateGroup.watch_day_id)
    await state.update_data(watch_day_by_id=watch_day_by_id)

    await callback.message.edit_text(
        text=nearest_match_day, reply_markup=admin_watch_day_keyboard.edit_meeting_keyboard()
    )
    # await state.update_data(watch_day_id=callback_data.id)
    await callback.answer()


@router.callback_query(F.data == "start_meeting_poll")
async def start_meeting_poll(callback: CallbackQuery, state: FSMContext):
    watch_day_state_data = await state.get_data()
    watch_day_info = watch_day_state_data['watch_day_by_id']
    print(f"{watch_day_info=}")
    watch_day_id = watch_day_info[0].watch_day_id
    tournament_name = watch_day_info[0].tournament_name
    located_match_day_name = watch_day_info[0].localed_match_day_name
    meeting_date = watch_day_info[0].meeting_date
    place_name = watch_day_info[0].place_name
    address = watch_day_info[0].address
    question = (f"СРОЧНОСБОР\n"
                f"{tournament_name}\n"
                f"{located_match_day_name}\n"
                f"\n"
                f"{meeting_date.strftime('%a, %d %b %H:%M')}"
                f"{place_name} - {address}")
    options = [
        PollOption(text="Иду", voter_count=0),
        PollOption(text="Не иду", voter_count=0)
    ]
    poll = Poll(
        id="1",
        question=question,
        options=options,
        is_anonymous=False,
        type='regular',
        allows_multiple_answers=False,
        total_voter_count=0,
        is_closed=True
    )

    # TODO: Придумать как убирать предыдущее сообщение

    await callback.bot.send_poll(
        chat_id=-1002374530977,
        question=question,
        options=["Иду", "Не иду"],
        is_anonymous=poll.is_anonymous
    )

    await callback.message.answer(
        text="Опрос отправлен",
        reply_markup=admin_watch_day_keyboard.main_admin_keyboard()
    )

    await callback.answer()

    # await callback.message.se(
    #     question=poll.question, options=["Иду", "Не иду"],
    #     is_anonymous=poll.is_anonymous,
    # )



@router.callback_query(F.data == "edit_watch_place")
async def process_go_button(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PlaceState.edit_watch_place)
    watch_day_state_data = await state.get_data()
    watch_day_info = watch_day_state_data['watch_day_by_id']
    print(f"{watch_day_info=}")
    watch_day_id = watch_day_info[0].watch_day_id

    await state.update_data(watch_day_id=watch_day_id)

    places_string = "<b>Выберите новое место просмотра</b>\n"
    places = match_day_manager.get_places()

    data_factories = [
        WatchPlaceChangeFactory(id=context.id) for context in places
    ]
    reply_keyboard = places_keyboard.places_editor_keyboard(
        data_factories, places
    )
    await callback.message.edit_text(
        text=places_string, reply_markup=reply_keyboard
    )
    await callback.answer()


@router.callback_query(WatchPlaceChangeFactory.filter(), PlaceState.edit_watch_place)
async def change_watch_place_process(
        callback: CallbackQuery, callback_data: WatchPlaceChangeFactory, state: FSMContext
):
    place_id = callback_data.id
    watch_day_state_data = await state.get_data()
    watch_day_id = watch_day_state_data['watch_day_id']

    try:
        match_day_manager.change_watch_day_place(watch_day_id=watch_day_id, place_id=place_id)
        await callback.message.edit_text(
            text=f"Место для встречи изменено, {place_id=}, {watch_day_id=}",
            reply_markup=admin_watch_day_keyboard.main_admin_keyboard()
        )
    except Exception:
        await callback.message.edit_text(
            text="Не удалось изменить место встречи",
            reply_markup=admin_watch_day_keyboard.main_admin_keyboard()
        )
    await callback.answer()


@router.callback_query(F.data == "cancel_meeting")
async def process_not_go_button(callback: CallbackQuery, state: FSMContext):
    watch_day_state_data = await state.get_data()
    watch_day_info = watch_day_state_data['watch_day_by_id'][0]
    watch_day_id = watch_day_info.watch_day_id
    watch_day_datetime = watch_day_info.meeting_date.strftime('%d_%m_%Y')

    watch_day_table = f"match_day_{watch_day_datetime}"

    print(f"{watch_day_info=}")
    try:
        match_day_manager.delete_watch_day(watch_day_id=watch_day_id, watch_day_table=watch_day_table)
        await callback.message.edit_text(
            text="Встреча отменена.", reply_markup=admin_watch_day_keyboard.main_admin_keyboard()
        )
    except Exception:
        await callback.message.edit_text(
            text="Не удалось отменить встречу",
            reply_markup=admin_watch_day_keyboard.main_admin_keyboard()
        )
    await callback.answer()


@router.callback_query(F.data == "show_visitors")
async def process_show_visitors(callback: CallbackQuery, state: FSMContext):
    watch_day_state_data = await state.get_data()
    watch_day_info = watch_day_state_data['watch_day_by_id']
    watch_day_table = f'match_day_{watch_day_info[0].meeting_date.strftime("%d_%m_%Y")}'

    print(watch_day_table)

    try:
        users = match_day_manager.show_visitors(watch_day_table=watch_day_table)

        users_string = "\n".join([f"@{user.username} - {user.user_role}" for user in users])

        await callback.message.edit_text(
            text=f"Показаны участники встречи\n{users_string}", reply_markup=admin_watch_day_keyboard.main_admin_keyboard()
        )
    except Exception:
        await callback.message.edit_text(
            text="Участники встречи не найдены",
            reply_markup=admin_watch_day_keyboard.main_admin_keyboard()
        )

    await callback.answer()


@router.callback_query(F.data == "back_to_main_menu")
async def process_menu_button(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Главное меню управления ботом.\n\nВыберите интересующую функцию.",
        reply_markup=admin_watch_day_keyboard.main_admin_keyboard()
    )
    await callback.answer()