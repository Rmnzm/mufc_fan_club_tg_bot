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
            user_id
    ):
        message_text = self.__create_text_message(context=context)

        print(f"Current state = {state}")
        await state.set_state(Form.waiting_for_button_press)
        await state.update_data(context=context)
        await self.bot.send_message(chat_id=user_id, text=message_text, reply_markup=invitation_keyboard)

        print(f"Current state = {await state.get_state()}")
        print(f"Current state data = {await state.get_data()}")

    @staticmethod
    def __create_text_message(context):
        match_name = context.get("match_day_name")
        place_name = context.get("place_name")
        address = context.get("address")
        meeting_date = context.get("meeting_date").strftime("%a, %d %b %H:%M")

        # TODO: переписать под макроподстановки и базовое сообщение из БД
        return (f"Матч\n"
                f"{match_name} \n"
                f"\n"
                f"приглашает Вас к просмотру\n"
                f"\n"
                f"{meeting_date}\n"
                f"{place_name}\n"
                f"{address}")

