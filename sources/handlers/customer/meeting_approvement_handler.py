import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from functions.kzn_reds_pg_manager import KznRedsPGManager
from functions.meeting_invites_manager import Form

logger = logging.getLogger(__name__)

router = Router()

match_day_manager = KznRedsPGManager()



@router.callback_query(Form.waiting_for_button_press, F.data == "approve_invitation")
async def process_button_press(callback: CallbackQuery, state: FSMContext):
    state_context = await state.get_data()
    print(state_context.get("context"))
    print(f"{callback}")
    context = state_context.get("context")

    try:
        match_day_manager.approve_watch_day_by_user_invitation_info(
            context.get("table_name"),
            callback.from_user.id,
            context.get("match_day_id")
        )
        await callback.message.edit_text("Супер! Ждем\nGG MU!")
    except Exception as e:
        await callback.message.edit_text("Не получилось зарегистировать на просмотр. Повторите позднее или обратитесь к организаторам")

    await callback.answer()
    await state.clear()


@router.callback_query(Form.waiting_for_button_press, F.data == "cancel_invitation")
async def process_button_press(callback: CallbackQuery, state: FSMContext):
    state_context = await state.get_data()
    print(state_context.get("context"))
    print(f"{callback}")
    context = state_context.get("context")
    try:
        match_day_manager.cancel_watch_day_by_user_invitation_info(
            context.get("table_name"),
            callback.from_user.id,
            context.get("match_day_id")
        )
        await callback.message.edit_text("Очень жаль. Увидимся в следующий раз")
    except Exception as e:
        await callback.message.edit_text("Не получилось отменить регистрацию на просмотр. Повторите позднее или обратитесь к организаторам")

    await callback.answer()
    await state.clear()