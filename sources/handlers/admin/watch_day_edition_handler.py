import datetime
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram.types import Poll, PollAnswer, PollOption

from callback_factory.callback_factory import (
    AdminMatchDayCallbackFactory,
    WatchPlaceChangeFactory,
)
from config.config import get_settings
from functions.admin_checker import AdminFilter
from functions.helpers.watch_day_helper import WatchDayHelper
from functions.schema_converter import SchemaConverter
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.admin_keyboard import AdminKeyboard
from keyboards.keyboard_generator import KeyboardGenerator
from lexicon.admin_lexicon_ru import (
    ERROR_ADMIN_LEXICON_RU,
    BASE_ADMIN_LEXICON_RU,
    ADMIN_MATCH_INVITE_POLL_OPTIONS,
)
from schemes.scheme import UsersSchema, NearestMeetingsSchema
from states.main_states import WatchDayInfoStateGroup

logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()
admin_watch_day_keyboard = AdminKeyboard()
places_keyboard = KeyboardGenerator()

match_day_manager = KznRedsPGManager()
schema_converter = SchemaConverter()


class PlaceState(StatesGroup):
    watch_day_id = State()
    delete_watch_day = State()
    edit_watch_place = State()


class PollStates(StatesGroup):
    watch_day_info = State()


@router.callback_query(AdminMatchDayCallbackFactory.filter(), AdminFilter())
async def process_scheduled_match_days_filter(
    callback: CallbackQuery,
    callback_data: AdminMatchDayCallbackFactory,
    state: FSMContext,
):
    try:
        logger.debug(
            f"Step process_scheduled_match_days_filter with context: {callback_data}"
        )
        watch_day_by_id = match_day_manager.get_watch_day_by_match_day_id(
            callback_data.id
        )

        nearest_match_day_message, watch_day_by_id_dict = WatchDayHelper().watch_day_by_id_context(watch_day_by_id)

        await state.set_state(WatchDayInfoStateGroup.watch_day_id)
        await state.update_data(watch_day_by_id=watch_day_by_id_dict)

        await callback.message.edit_text(
            text=nearest_match_day_message,
            reply_markup=admin_watch_day_keyboard.edit_meeting_keyboard(),
        )
        logger.info(
            f"Successfully received scheduled match days. {nearest_match_day_message}"
        )
    except Exception as error:
        logger.error(f"Failed to fetch nearest match day. Err: {error}")
        await callback.message.edit_text(
            text=ERROR_ADMIN_LEXICON_RU["failed_process_scheduled_match_days_filter"],
            reply_markup=admin_watch_day_keyboard.main_admin_keyboard(),
        )

    await callback.answer()


@router.callback_query(F.data == "start_meeting_poll", AdminFilter())
async def start_meeting_poll(callback: CallbackQuery, state: FSMContext):
    try:
        logger.debug(f"Step start_meeting_poll with context: {callback.data}")

        watch_day_state_data = await state.get_data()
        watch_day_info = watch_day_state_data["watch_day_by_id"]
        logger.info(f"{watch_day_info=}")

        watch_day_id = watch_day_info[0].get("watch_day_id")

        question = _create_poll_question(watch_day_info)

        await state.set_state(PollStates.watch_day_info)
        await state.update_data(watch_day_info=watch_day_info)

        current_state = await state.get_state()
        logger.info(f"{current_state=}")
        current_state_data = await state.get_data()
        logger.info(f"{current_state_data=}")

        options = _create_poll_options(watch_day_id)
        poll = _create_chat_poll_obj(question, options)

        # Aiogram/Telegram has no methods to delete previous messages older than 48 hours. It can EDIT current message

        await callback.bot.send_poll(
            chat_id=-int(settings.tg_kzn_reds_chat_id),
            question=question,
            options=[
                ADMIN_MATCH_INVITE_POLL_OPTIONS["agree"],
                ADMIN_MATCH_INVITE_POLL_OPTIONS["cancel"],
            ],
            is_anonymous=poll.is_anonymous,
        )

        await callback.message.edit_text(
            text=BASE_ADMIN_LEXICON_RU["start_meeting_poll"],
            reply_markup=admin_watch_day_keyboard.main_admin_keyboard(),
        )
        logger.info(f"Meeting poll successfully sent on chat.")

    except Exception as error:
        logger.error(f"Failed to send meeting poll. Err: {error}")
        await callback.message.edit_text(
            text=ERROR_ADMIN_LEXICON_RU["failed_start_meeting_poll"],
            reply_markup=admin_watch_day_keyboard.main_admin_keyboard(),
        )

    await callback.answer()


@router.poll_answer()
async def poll_answers(poll_answer: PollAnswer, state: FSMContext):
    try:
        logger.debug(f"Step poll_answer from user {poll_answer.user.id}")
        logger.debug(f"Step poll_answer={poll_answer.__dict__}")

        state_data = await state.get_data()
        watch_day_info = state_data.get("watch_day_info")

        current_state = await state.get_state()
        logger.debug(f"Step poll_answers{current_state=}")
        current_state_data = await state.get_data()
        logger.debug(f"Step poll_answers {current_state_data=}")

        option_ids = ",".join(map(str, poll_answer.option_ids))

        user_schema = _create_poll_answer_user_schema(poll_answer)

        logger.info(
            f"User info = {poll_answer.user.username=}, {poll_answer.user.first_name=}, {poll_answer.user.last_name}"
            f"User {poll_answer.user.id} voted in poll {poll_answer.poll_id} with options {option_ids}",
        )

        logger.debug(f"Step poll_answers {watch_day_info=}")

        match_day_manager.register_user(
            user_tg_id=poll_answer.user.id, user_schema=user_schema
        )

        if option_ids == "0":
            _register_user_poll_answer(poll_answer, watch_day_info)
        logger.info(f"Successfully processed user poll answer: {poll_answer}")
    except Exception as error:
        logger.error(f"Failed to process poll answer. Err: {error}")


@router.callback_query(F.data == "edit_watch_place", AdminFilter())
async def process_go_button(callback: CallbackQuery, state: FSMContext):
    try:
        logger.debug(f"Step process_go_button with context: {callback.data}")
        await state.set_state(PlaceState.edit_watch_place)
        watch_day_state_data = await state.get_data()
        watch_day_info = watch_day_state_data["watch_day_by_id"]
        logger.debug(f"Step process_go_button {watch_day_info=}")
        watch_day_id = watch_day_info[0].watch_day_id

        await state.update_data(watch_day_id=watch_day_id)

        places = match_day_manager.get_places()

        data_factories = [WatchPlaceChangeFactory(id=context.id) for context in places]
        reply_keyboard = places_keyboard.places_editor_keyboard(data_factories, places)
        await callback.message.edit_text(
            text=BASE_ADMIN_LEXICON_RU["process_go_button"], reply_markup=reply_keyboard
        )
        logger.info(f"Successfully processed go button")
    except Exception as error:
        logger.error(f"Failed to processing go button. Err: {error}")
        await callback.message.edit_text(
            text=ERROR_ADMIN_LEXICON_RU["failed_process_go_button"],
            reply_markup=admin_watch_day_keyboard.main_admin_keyboard(),
        )
    await callback.answer()


@router.callback_query(
    WatchPlaceChangeFactory.filter(), PlaceState.edit_watch_place, AdminFilter()
)
async def change_watch_place_process(
    callback: CallbackQuery, callback_data: WatchPlaceChangeFactory, state: FSMContext
):
    place_id = callback_data.id
    watch_day_state_data = await state.get_data()
    watch_day_id = watch_day_state_data["watch_day_id"]

    try:
        logger.debug(f"Step change_watch_place_process with context: {callback_data}")
        match_day_manager.change_watch_day_place(
            watch_day_id=watch_day_id, place_id=place_id
        )
        await callback.message.edit_text(
            text=BASE_ADMIN_LEXICON_RU["change_watch_place_process"],
            reply_markup=admin_watch_day_keyboard.main_admin_keyboard(),
        )
        logger.info(f"Successfully changed meeting place place on {watch_day_id=}")
    except Exception as error:
        logger.error(f"Failed to change meeting place. Err: {error}")
        await callback.message.edit_text(
            text=ERROR_ADMIN_LEXICON_RU["failed_change_watch_place_process"],
            reply_markup=admin_watch_day_keyboard.main_admin_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data == "cancel_meeting", AdminFilter())
async def process_cancel_meeting(callback: CallbackQuery, state: FSMContext):
    watch_day_state_data = await state.get_data()
    watch_day_info = watch_day_state_data["watch_day_by_id"][0]
    watch_day_id = watch_day_info.watch_day_id
    watch_day_datetime = watch_day_info.meeting_date.strftime("%d_%m_%Y")

    watch_day_table = f"match_day_{watch_day_datetime}"

    logger.debug(f"Step process_cancel_meeting {watch_day_info=}")
    try:
        logger.debug(f"Step process_cancel_meeting with context: {callback.data}")
        match_day_manager.delete_watch_day(
            watch_day_id=watch_day_id, watch_day_table=watch_day_table
        )
        await callback.message.edit_text(
            text=BASE_ADMIN_LEXICON_RU["process_cancel_meeting"],
            reply_markup=admin_watch_day_keyboard.main_admin_keyboard(),
        )
        logger.info(f"Successfully canceled meeting with {watch_day_id=}")
    except Exception as error:
        logger.error(f"Failed to cancel meeting. Err: {error}")
        await callback.message.edit_text(
            text=ERROR_ADMIN_LEXICON_RU["failed_process_cancel_meeting"],
            reply_markup=admin_watch_day_keyboard.main_admin_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data == "show_visitors", AdminFilter())
async def process_show_visitors(callback: CallbackQuery, state: FSMContext):
    watch_day_state_data = await state.get_data()
    watch_day_info = watch_day_state_data["watch_day_by_id"]

    logger.info(f"show visitors - {watch_day_info=}")
    watch_day_datetime = datetime.datetime.strptime(
        watch_day_info[0]["meeting_date"], "%Y-%m-%dT%H:%M:%S"
    )

    watch_day_table = f'match_day_{watch_day_datetime.strftime("%d_%m_%Y")}'

    logger.info(watch_day_table)

    try:
        logger.debug(f"Step process_show_visitors with context: {callback.data}")
        users = match_day_manager.show_visitors(watch_day_table=watch_day_table)

        users_string = "\n".join(
            [f"@{user.username} - {user.user_role}" for user in users]
        )

        await callback.message.edit_text(
            text=BASE_ADMIN_LEXICON_RU["process_show_visitors"].format(
                users_string=users_string
            ),
            reply_markup=admin_watch_day_keyboard.main_admin_keyboard(),
        )
        logger.info(f"Successfully received and showed approved users. {users_string=}")
    except Exception as error:
        logger.error(f"Failed to receive or show approved users. Err: {error}")
        await callback.message.edit_text(
            text=ERROR_ADMIN_LEXICON_RU["failed_process_show_visitors"],
            reply_markup=admin_watch_day_keyboard.main_admin_keyboard(),
        )

    await callback.answer()


@router.callback_query(F.data == "back_to_main_menu", AdminFilter())
async def process_menu_button(callback: CallbackQuery):
    await callback.message.edit_text(
        text=BASE_ADMIN_LEXICON_RU["main_admin_menu"],
        reply_markup=admin_watch_day_keyboard.main_admin_keyboard(),
    )
    await callback.answer()


def _create_poll_question(watch_day_info):
    tournament_name = watch_day_info[0].get("tournament_name")
    located_match_day_name = watch_day_info[0].get("localed_match_day_name")
    meeting_date = watch_day_info[0].get("meeting_date")
    place_name = watch_day_info[0].get("place_name")
    address = watch_day_info[0].get("address")
    question = (
        f"СРОЧНОСБОР\n"
        f"{tournament_name}\n"
        f"{located_match_day_name}\n"
        f"\n"
        f"{meeting_date}\n"
        f"{place_name} - {address}"
    )

    return question


def _create_poll_options(watch_day_id: int):
    options = [
        PollOption(
            text=ADMIN_MATCH_INVITE_POLL_OPTIONS["agree"],
            voter_count=0,
            watch_day_id=watch_day_id,
        ),
        PollOption(
            text=ADMIN_MATCH_INVITE_POLL_OPTIONS["cancel"],
            voter_count=0,
            watch_day_id=watch_day_id,
        ),
    ]
    return options


def _create_chat_poll_obj(question, options):
    poll = Poll(
        id="1",
        question=question,
        options=options,
        is_anonymous=False,
        type="regular",
        allows_multiple_answers=False,
        total_voter_count=0,
        is_closed=True,
    )
    return poll


def _create_poll_answer_user_schema(poll_answer):
    user_schema = UsersSchema(
        username=poll_answer.user.username,
        user_role="USER",
        first_name=poll_answer.user.first_name if poll_answer.user.first_name else None,
        last_name=poll_answer.user.last_name if poll_answer.user.last_name else None,
    )
    return user_schema


def _register_user_poll_answer(poll_answer, watch_day_info):
    try:
        watch_day_list = NearestMeetingsSchema(**watch_day_info[0])
        match_day_manager.register_user_to_watch(
            user_id=poll_answer.user.id,
            watch_day_id=watch_day_list.watch_day_id,
            match_day_id=watch_day_list.match_day_id,
            place_id=watch_day_list.place_id,
        )
    except Exception as error:
        logger.exception(f"Failed to register user to watch. Err: {error}")
