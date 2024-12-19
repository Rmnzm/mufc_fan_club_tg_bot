from typing import Iterable, List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callback_factory.callback_factory import MatchDayCallbackFactory, AdminMatchDayCallbackFactory
from schemes.scheme import NearestMeetingsSchema


class KeyboardGenerator:
    def __init__(self):
        pass

    def watch_day_keyboard(self, data_factories: List[MatchDayCallbackFactory], buttons_info: list[NearestMeetingsSchema]):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[self.__button(factory_data, buttons_info)] for factory_data in data_factories],
            resize_keyboard=True
        )
        return keyboard

    def admin_watch_day_keyboard(self, data_factories: List[AdminMatchDayCallbackFactory], buttons_info: list[NearestMeetingsSchema]):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[self.__button(factory_data, buttons_info)] for factory_data in data_factories],
            resize_keyboard=True
        )
        return keyboard


    @staticmethod
    def __button(
            callback_data: MatchDayCallbackFactory | AdminMatchDayCallbackFactory,
            button_data: list[NearestMeetingsSchema]
    ) -> InlineKeyboardButton:
        try:
            btn_data = list(filter(lambda i: callback_data.id == i.id, button_data))
            button_name = f"{btn_data[0].meeting_date.strftime('%a, %d %b %H:%M')} {btn_data[0].localed_match_day_name}"
            button = InlineKeyboardButton(
                text=button_name, callback_data=callback_data.pack()
            )
            return button
        except ValueError:
            print(len('watch_days:5:30/12/2024:Манчестер Юнайтед -- ФК Буде/Глимт'.encode()))