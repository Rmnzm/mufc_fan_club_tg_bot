from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class Form(StatesGroup):
    waiting_for_button_press = State()

# 715078441

class MeetingInvitesManager:

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_message(
            self,
            # user_id,
            # text,
            state: FSMContext,
            context
    ):
        inline_buttons = [
            [InlineKeyboardButton(text="Кнопка 1", callback_data="button1")],
            [InlineKeyboardButton(text="Кнопка 2", callback_data="button2")],
            [InlineKeyboardButton(text="Кнопка 3", callback_data="button3")]
        ]
        inline_keyboard = InlineKeyboardMarkup(inline_keyboard=inline_buttons)
        text = "Приветв"
        user_id = 715078441

        print(f"Current state = {state}")
        await state.set_state(Form.waiting_for_button_press)
        await state.update_data(context=context)
        await self.bot.send_message(chat_id=user_id, text=text, reply_markup=inline_keyboard)

        print(f"Current state = {await state.get_state()}")
        print(f"Current state data = {await state.get_data()}")

