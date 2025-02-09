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
    button_text = callback.data
    await callback.message.edit_text(f"Вы нажали: {button_text}")
    await callback.answer()
    await state.clear()


@router.callback_query(Form.waiting_for_button_press, F.data == "cancel_invitation")
async def process_button_press(callback: CallbackQuery, state: FSMContext):
    state_context = await state.get_data()
    print(state_context.get("context"))
    print(f"{callback}")
    button_text = callback.data
    await callback.message.edit_text(f"Вы нажали: {button_text}")
    await callback.answer()
    await state.clear()