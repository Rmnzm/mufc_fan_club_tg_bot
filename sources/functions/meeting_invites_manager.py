from datetime import datetime
import logging

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.meeting_approvement_keyboard import MeetingApprovementKeyboard
from lexicon.watch_day_lexicon_ru import WATCH_DAY_LEXICON_RU
from functions.helpers.watch_day_helper import WatchDayHelper

logger = logging.getLogger(__name__)

invitation_keyboard = MeetingApprovementKeyboard().main_approvement_keyboard()

kzn_reds_pg_manager = KznRedsPGManager()


class Form(StatesGroup):
    waiting_for_button_press = State()


class MeetingInvitesManager:

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_message(self, state: FSMContext, context, user_id):
        logger.debug(f"Step send_message.")
        message_text = self.__create_text_message(context=context)

        logger.debug(f"Step send_message. Current state = {state}")
        await state.set_state(Form.waiting_for_button_press)
        await state.update_data(context=context)
        await self.bot.send_message(
            chat_id=user_id, text=message_text, reply_markup=invitation_keyboard
        )

        logger.debug(f"Step send_message. Current state = {await state.get_state()}")
        logger.debug(
            f"Step send_message. Current state data = {await state.get_data()}"
        )

    @staticmethod
    def __create_text_message(context):
        match_name = context.get("match_day_name")
        place_name = context.get("place_name")
        address = context.get("address")
        match_day_datetime = datetime.strptime(context.get("meeting_date"), "%a, %d %b %H:%M")
        date_str, time_str, gathering_str = WatchDayHelper.format_match_date(match_day_datetime)
        return WATCH_DAY_LEXICON_RU["meeting_invite_message"].format(
            match_name=match_name,
            date_str=date_str,
            time_str=time_str,
            gathering_str=gathering_str,
            place_name=place_name,
            address=address,
        )
