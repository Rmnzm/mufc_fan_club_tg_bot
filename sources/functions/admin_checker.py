from typing import Any

from aiogram.types import Message
from aiogram.filters import Filter

from config.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

ADMIN_IDs = settings.admin_ids


class AdminFilter(Filter):
    async def __call__(self, message: Message) -> bool | dict[str, Any]:
        if str(message.from_user.id) in settings.admin_ids:
            return True
        else:
            await message.answer("У вас нет доступа к этой команде.")
            return False