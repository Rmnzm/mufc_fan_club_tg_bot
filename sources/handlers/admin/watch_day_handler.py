import logging
from pydantic import ValidationError

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery

from callback_factory.callback_factory import (
    AdminCreateWatchDayCallbackFactory,
    PlacesFactory,
)
from config.config import get_settings
from functions.admin_checker import AdminFilter
from functions.kzn_reds_pg_manager import KznRedsPGManager
from functions.schema_converter import SchemaConverter
from handlers.admin.base_admin_handler import admin_keyboard
from keyboards.admin_keyboard import AdminKeyboard
from keyboards.keyboard_generator import KeyboardGenerator
from keyboards.watch_day_keyboard import WatchDayKeyboard
from schemes.scheme import MatchDaySchema
from lexicon.admin_lexicon_ru import (
    ADMIN_WATCH_DAY_HANDLER_LEXICON_RU,
    ADMIN_WATCH_DAY_HANDLER_ERROR_LEXICON_RU,
)

logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()

match_day_manager = KznRedsPGManager()
schema_converter = SchemaConverter()

watch_day_keyboard = WatchDayKeyboard().watch_day_keyboard()
main_keyboard = AdminKeyboard()
keyboard_generator = KeyboardGenerator()


class WatchDay(StatesGroup):
    choose_match_day = State()
    choose_place = State()


@router.callback_query(F.data == "add_watch_day", AdminFilter())
async def watch_day_register(callback: CallbackQuery, state: FSMContext):
    try:
        logger.debug(f"Step watch_day_register with context {callback.data}")
        await state.set_state(WatchDay.choose_match_day)
        nearest_matches = match_day_manager.get_nearest_match_day()

        if nearest_matches:
            logger.info(f"{nearest_matches=}")
            data_factories = [
                AdminCreateWatchDayCallbackFactory(id=context.event_id)
                for context in nearest_matches
            ]
            reply_keyboard = keyboard_generator.admin_create_watch_day_keyboard(
                data_factories, nearest_matches, add_watch_day=False
            )
            await callback.message.edit_text(
                text=ADMIN_WATCH_DAY_HANDLER_LEXICON_RU["add_watch_day"],
                reply_markup=reply_keyboard,
            )
        else:
            await callback.message.edit_text(
                text=ADMIN_WATCH_DAY_HANDLER_LEXICON_RU["no_nearest_matches"],
                reply_markup=main_keyboard.main_admin_keyboard(),
            )
        logger.info(
            f"Successfully reacted on watch_day_register action by user {callback.from_user.id}"
        )
    except ValidationError as error:
        logger.error(f"Err: {error.with_traceback}. Validation error: {error.errors()}")
        await callback.message.edit_text(
            text=ADMIN_WATCH_DAY_HANDLER_ERROR_LEXICON_RU["watch_day_register_error"],
            reply_markup=main_keyboard.main_admin_keyboard(),
        )
    except Exception as error:
        logger.error(f"Failed to react on action watch_day_register. Err: {error.with_traceback}")
        await callback.message.edit_text(
            text=ADMIN_WATCH_DAY_HANDLER_ERROR_LEXICON_RU["watch_day_register_error"],
            reply_markup=main_keyboard.main_admin_keyboard(),
        )
    await callback.answer()


@router.callback_query(AdminCreateWatchDayCallbackFactory.filter(), AdminFilter())
async def choose_place(
    callback: CallbackQuery,
    callback_data: AdminCreateWatchDayCallbackFactory,
    state: FSMContext,
):
    try:
        logger.debug(
            f"Step choose_place with context {callback.data} and {callback_data=}"
        )
        match_day_by_id = match_day_manager.get_match_day_by_event_id(callback_data.id)

        match_day_by_id_dict = schema_converter.convert_model_to_dict(
            match_day_by_id[0]
        )
        match_day_by_id_dict["start_timestamp"] = match_day_by_id_dict[
            "start_timestamp"
        ].isoformat()
        match_day_by_id_dict["match_status"] = match_day_by_id_dict[
            "match_status"
        ]

        await state.set_state(WatchDay.choose_place)
        await state.update_data(match_day_by_id=match_day_by_id_dict)

        places = match_day_manager.get_places()

        data_factories = [PlacesFactory(id=context.id) for context in places]
        reply_keyboard = keyboard_generator.places_keyboard(data_factories, places)
        await callback.message.edit_text(
            text=ADMIN_WATCH_DAY_HANDLER_LEXICON_RU["choose_place"],
            reply_markup=reply_keyboard,
        )
    except Exception as error:
        logger.error(f"Failed to react on choose_place action. Err: {error}")
        await callback.message.edit_text(
            text=ADMIN_WATCH_DAY_HANDLER_ERROR_LEXICON_RU["choose_place_error"],
            reply_markup=main_keyboard.main_admin_keyboard(),
        )
    await callback.answer()


@router.callback_query(PlacesFactory.filter(), WatchDay.choose_place, AdminFilter())
async def registrate_meeting(
    callback: CallbackQuery, callback_data: PlacesFactory, state: FSMContext
):
    current_state_data = await state.get_data()
    place_id = callback_data.id

    try:
        logger.debug(f"Step registrate_meeting with context={callback.data}")
        match_day_data = MatchDaySchema(**current_state_data["match_day_by_id"])
        match_day_manager.add_watch_day(match_day_data, place_id)
        await callback.message.edit_text(
            text=ADMIN_WATCH_DAY_HANDLER_LEXICON_RU["registrate_meeting"],
            reply_markup=admin_keyboard.main_admin_keyboard(),
        )
        logger.info(
            f"Successfully registered meeting on match_day_id={match_day_data.id}"
        )

    except Exception as error:
        logger.error(f"Failed to react on action registrate_meeting. Err: {error}")
        await callback.message.edit_text(
            text=ADMIN_WATCH_DAY_HANDLER_ERROR_LEXICON_RU["registrate_meeting_error"],
            reply_markup=main_keyboard.main_admin_keyboard(),
        )
    await callback.answer()

    await state.clear()
