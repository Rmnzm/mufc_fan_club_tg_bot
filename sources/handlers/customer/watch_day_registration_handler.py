import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from callback_factory.callback_factory import MatchDayCallbackFactory
from config.config import get_settings
from functions.kzn_reds_pg_manager import KznRedsPGManager
from functions.helpers.watch_day_helper import WatchDayHelper
from functions.schema_converter import SchemaConverter
from keyboards.main_keyboard import MainKeyboard
from keyboards.watch_day_keyboard import WatchDayKeyboard
from lexicon.base_lexicon_ru import BASE_LEXICON_RU
from lexicon.customer_lexicon_ru import CUSTOMER_LEXICON_RU, CUSTOMER_ERROR_LEXICON_RU
from schemes.scheme import NearestMeetingsSchema
from states.main_states import WatchDayUserRegistrationStateGroup

logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()

main_keyboard = MainKeyboard()
watch_day_keyboard = WatchDayKeyboard()

match_day_manager = KznRedsPGManager()
schema_converter = SchemaConverter()


@router.callback_query(MatchDayCallbackFactory.filter())
async def process_scheduled_match_days_filter(
    callback: CallbackQuery, callback_data: MatchDayCallbackFactory, state: FSMContext
):
    try:
        logger.debug(f"Step MatchDayCallbackFactory with context = {callback_data}")
        watch_day_by_id = match_day_manager.get_watch_day_by_match_day_id(
            callback_data.id
        )

        nearest_match_day_message, watch_day_by_id_dict = (
            WatchDayHelper().watch_day_by_id_context(watch_day_by_id)
        )

        logger.debug(
            f"Step process_scheduled_match_days_filter. watch_day_registration_handler - {watch_day_by_id_dict=}"
        )

        await state.set_state(WatchDayUserRegistrationStateGroup.watch_day_id)

        await callback.message.edit_text(
            text=nearest_match_day_message,
            reply_markup=watch_day_keyboard.approve_meeting_keyboard(),
        )
        await state.update_data(
            watch_day_id=watch_day_by_id[0].watch_day_id,
            match_day_id=callback_data.id,
            place_id=watch_day_by_id[0].place_id,
        )
    except Exception as e:
        logger.error(
            f"Error due fetching scheduled match day by id = {callback_data.id}. Err: {e}"
        )
        await callback.message.edit_text(
            text=CUSTOMER_ERROR_LEXICON_RU["error_fetching_scheduled_match_days"],
            reply_markup=main_keyboard.main_keyboard(),
        )
    await callback.answer()


@router.callback_query(
    F.data == "go_button", WatchDayUserRegistrationStateGroup.watch_day_id
)
async def process_go_button(callback: CallbackQuery, state: FSMContext):
    try:
        state_data = await state.get_data()
        user_id = callback.from_user.id
        logger.debug(f"Step {F.data=} by {user_id}")

        match_day_manager.finish_registration(
            user_id=user_id, match_day_id=state_data["match_day_id"], is_approved=True
        )

        await callback.message.edit_text(
            text=CUSTOMER_LEXICON_RU["first_approve_invitation"],
            reply_markup=main_keyboard.main_keyboard(),
        )
    except Exception as e:
        logger.error(f"Erro due first approving meeting. Err: {e}")
        await callback.message.edit_text(
            text=CUSTOMER_ERROR_LEXICON_RU["error_first_approve_invitation"],
            reply_markup=main_keyboard.main_keyboard(),
        )
    await callback.answer()


@router.callback_query(
    F.data == "not_go_button", WatchDayUserRegistrationStateGroup.watch_day_id
)
async def process_not_go_button(callback: CallbackQuery, state: FSMContext):
    try:
        state_data = await state.get_data()
        user_id = callback.from_user.id
        logger.debug(f"Step {F.data=} by {user_id=}")

        match_day_manager.finish_registration(
            user_id=user_id, match_day_id=state_data["match_day_id"], is_canceled=True
        )
        await callback.message.edit_text(
            text=CUSTOMER_LEXICON_RU["first_cancel_invitation"],
            reply_markup=main_keyboard.main_keyboard(),
        )
    except Exception as e:
        logger.error(f"Error due canceling meeting. Err: {e}")
        await callback.message.edit_text(
            text=CUSTOMER_ERROR_LEXICON_RU["error_first_cancel_invitation"],
            reply_markup=main_keyboard.main_keyboard(),
        )
    await callback.answer()


@router.callback_query(
    F.data == "menu_button", WatchDayUserRegistrationStateGroup.watch_day_id
)
async def process_menu_button(callback: CallbackQuery):
    logger.debug(
        f"Step {F.data=} with context = {WatchDayUserRegistrationStateGroup.watch_day_id}"
    )
    await callback.message.edit_text(
        text=BASE_LEXICON_RU["/start"], reply_markup=main_keyboard.main_keyboard()
    )
    await callback.answer()
