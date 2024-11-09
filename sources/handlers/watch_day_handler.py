import logging

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from config.config import get_settings
from functions.match_day_manager import MatchDayManager

logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()

match_day_manager = MatchDayManager()


@router.callback_query(F.data == "nearest_match_day")
async def watch_day_handler(callback: CallbackQuery):
    nearest_match_day = match_day_manager.get_nearest_match_day()

    await callback.message.edit_text(text=f"Добавлена встреча на ближайший матч\n\n{nearest_match_day}")
    await callback.answer()
