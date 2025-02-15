from aiogram import types

from config.config import get_settings

settings = get_settings()

ADMIN_IDs = settings.admin_ids


def admin_required(func):
    async def wrapper(message: types.Message, *args, **kwargs):
        print(f"{str(message.from_user.id) not in ADMIN_IDs=}")
        if str(message.from_user.id) in settings.admin_ids:
            return await func(message, *args, **kwargs)
        else:
            await message.answer("У вас нет доступа к этой команде.")

    return wrapper