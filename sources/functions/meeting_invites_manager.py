from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.meeting_approvement_keyboard import MeetingApprovementKeyboard

invitation_keyboard = MeetingApprovementKeyboard().main_approvement_keyboard()

kzn_reds_pg_manager = KznRedsPGManager()

class Form(StatesGroup):
    waiting_for_button_press = State()


class MeetingInvitesManager:

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_message(
            self,
            state: FSMContext,
            context,
            match_day_id
    ):
        text = "Приветв"
        user_id = 715078441
        users_to_send = kzn_reds_pg_manager.get_users_to_send_invitations(
            match_day_id=match_day_id
        )

        print(f"Current state = {state}")
        await state.set_state(Form.waiting_for_button_press)
        await state.update_data(context=context)
        await self.bot.send_message(chat_id=user_id, text=text, reply_markup=invitation_keyboard)

        print(f"Current state = {await state.get_state()}")
        print(f"Current state data = {await state.get_data()}")

