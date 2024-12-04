from typing import Iterable, List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData


class MatchDayCallbackFactory(CallbackData, prefix='watch_days'):
    id: int
    date: str
    match_name: str


class KeyboardGenerator:
    def __init__(self):
        pass

    def watch_day_keyboard(self, data: List[MatchDayCallbackFactory]):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[self.__button(callback_data)] for callback_data in data],
            resize_keyboard=True
        )
        return keyboard

    @staticmethod
    def __button(callback_data) -> InlineKeyboardButton:
        try:
            button = InlineKeyboardButton(
                text=f"{callback_data.date} {callback_data.match_name}", callback_data=callback_data.pack()
            )
            return button
        except ValueError:
            print(len('watch_days:5:30/12/2024:Манчестер Юнайтед -- ФК Буде/Глимт'.encode()))