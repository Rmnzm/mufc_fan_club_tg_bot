import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from functions.kzn_reds_pg_manager import KznRedsPGManager
from functions.meeting_invites_manager import Form
from lexicon.customer_lexicon_ru import CUSTOMER_LEXICON_RU, CUSTOMER_ERROR_LEXICON_RU

logger = logging.getLogger(__name__)

router = Router()

match_day_manager = KznRedsPGManager()



@router.callback_query(Form.waiting_for_button_press, F.data == "approve_invitation")
async def process_button_approve_invitation_press(callback: CallbackQuery, state: FSMContext):
    state_context = await state.get_data()
    context = state_context.get("context")
    logger.debug(f"Step {F.data=} with {context=}")

    try:
        match_day_manager.approve_watch_day_by_user_invitation_info(
            context.get("table_name"),
            callback.from_user.id,
            context.get("match_day_id")
        )
        await callback.message.edit_text(text=CUSTOMER_LEXICON_RU["approve_invitation"])
        logger.info(
            f"Successfully approved invitation on {context.get('match_day_id')} by user = {callback.from_user.id}"
        )
    except Exception as e:
        await callback.message.edit_text(text=CUSTOMER_ERROR_LEXICON_RU["error_approve_invitation"])
        logger.error(f"Error due to approving invitation. Err: {e}")

    await callback.answer()
    await state.clear()


@router.callback_query(Form.waiting_for_button_press, F.data == "cancel_invitation")
async def process_button_cancel_invitation_press(callback: CallbackQuery, state: FSMContext):
    state_context = await state.get_data()
    context = state_context.get("context")
    logger.debug(f"Step {F.data=} with {context=}")

    try:
        match_day_manager.cancel_watch_day_by_user_invitation_info(
            context.get("table_name"),
            callback.from_user.id,
            context.get("match_day_id")
        )
        await callback.message.edit_text(text=CUSTOMER_LEXICON_RU["cancel_invitation"])
        logger.info(
            f"Successfully canceled invitation on {context.get('match_day_id')} by user = {callback.from_user.id}"
        )
    except Exception as e:
        await callback.message.edit_text(text=CUSTOMER_ERROR_LEXICON_RU["error_cancel_invitation"])
        logger.error(f"Error due to canceling invitation. Err: {e}")

    await callback.answer()
    await state.clear()