from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.meeting_approvement_keyboard import MeetingApprovementKeyboard

invitation_keyboard = MeetingApprovementKeyboard().main_approvement_keyboard()

class Form(StatesGroup):
    waiting_for_button_press = State()


class MeetingInvitesManager:

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_message(
            self,
            state: FSMContext,
            context
    ):
        text = "Приветв"
        user_id = 715078441

        print(f"Current state = {state}")
        await state.set_state(Form.waiting_for_button_press)
        await state.update_data(context=context)
        await self.bot.send_message(chat_id=user_id, text=text, reply_markup=invitation_keyboard)

        print(f"Current state = {await state.get_state()}")
        print(f"Current state data = {await state.get_data()}")

