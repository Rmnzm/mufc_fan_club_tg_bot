from aiogram.filters import Filter
from aiogram.types import Message


class AllowedUsersFilter(Filter):
    def __init__(self, allowed_users):
        self.allowed_users = allowed_users

    async def __call__(self, message: Message, **kwargs):
        return str(message.from_user.id) in self.allowed_users
