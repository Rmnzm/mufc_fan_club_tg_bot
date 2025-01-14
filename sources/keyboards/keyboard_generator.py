from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callback_factory.callback_factory import MatchDayCallbackFactory, AdminMatchDayCallbackFactory, \
    AdminCreateWatchDayCallbackFactory, PlacesFactory, PlacesEditorFactory
from schemes.scheme import NearestMeetingsSchema, MatchDaySchema, PlacesSchema


class KeyboardGenerator:
    def __init__(self):
        pass

    def watch_day_keyboard(
            self, data_factories: List[MatchDayCallbackFactory], buttons_info: list[NearestMeetingsSchema]
    ):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[self.__button(factory_data, buttons_info)] for factory_data in data_factories],
            resize_keyboard=True
        )
        return keyboard

    def admin_watch_day_keyboard(
            self, data_factories: List[AdminMatchDayCallbackFactory],
            buttons_info: list[NearestMeetingsSchema],
            add_watch_day: bool = False
    ):
        inline_keyboard = [[self.__button(factory_data, buttons_info)] for factory_data in data_factories]
        if add_watch_day:
            inline_keyboard.append([InlineKeyboardButton(
                    text="Добавить просмотр", callback_data="add_watch_day"
                )])
        back_to_main_menu = InlineKeyboardButton(
            text="Назад в меню", callback_data="back_to_main_menu"
        )
        inline_keyboard.append([back_to_main_menu])
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=inline_keyboard,
            resize_keyboard=True
        )
        return keyboard


    def admin_create_watch_day_keyboard(
            self, data_factories: List[AdminCreateWatchDayCallbackFactory],
            buttons_info: list[MatchDaySchema],
            add_watch_day: bool = False
    ):
        inline_keyboard = [[self.__button_2(factory_data, buttons_info)] for factory_data in data_factories]
        if add_watch_day:
            inline_keyboard.append([InlineKeyboardButton(
                    text="Добавить просмотр", callback_data="add_watch_day"
                )])
        back_to_main_menu = InlineKeyboardButton(
            text="Назад в меню", callback_data="back_to_main_menu"
        )
        inline_keyboard.append([back_to_main_menu])
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=inline_keyboard,
            resize_keyboard=True
        )
        return keyboard


    def places_keyboard(self, data_factories: List[PlacesFactory], buttons_info: List[PlacesSchema]):
        inline_keyboard = [[self.__button_3(factory_data, buttons_info)] for factory_data in data_factories]
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=inline_keyboard,
            resize_keyboard=True
        )
        return keyboard


    def places_editor_keyboard(self, data_factories: List[PlacesEditorFactory], buttons_info: List[PlacesSchema]):
        inline_keyboard = [
            [self.__place_button(factory_data, buttons_info)] for factory_data in data_factories
        ]
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=inline_keyboard,
            resize_keyboard=True
        )
        return keyboard


    @staticmethod
    def __button(
            callback_data: MatchDayCallbackFactory | AdminMatchDayCallbackFactory,
            button_data: list[NearestMeetingsSchema]
    ) -> InlineKeyboardButton:
        try:
            btn_data = list(filter(lambda i: callback_data.id == i.match_day_id, button_data))
            button_name = f"{btn_data[0].meeting_date.strftime('%a, %d %b %H:%M')} {btn_data[0].localed_match_day_name}"
            button = InlineKeyboardButton(
                text=button_name, callback_data=callback_data.pack()
            )
            return button
        except ValueError:
            raise

    @staticmethod
    def __button_2(
            callback_data: MatchDayCallbackFactory | AdminCreateWatchDayCallbackFactory,
            button_data: list[MatchDaySchema]
    ) -> InlineKeyboardButton:
        try:
            btn_data = list(filter(lambda i: callback_data.id == i.id, button_data))
            button_name = f"{btn_data[0].start_timestamp.strftime('%a, %d %b %H:%M')} {btn_data[0].localed_match_day_name}"
            button = InlineKeyboardButton(
                text=button_name, callback_data=callback_data.pack()
            )
            return button
        except ValueError:
            raise


    @staticmethod
    def __button_3(
            callback_data: PlacesFactory,
            button_data: list[PlacesSchema]
    ) -> InlineKeyboardButton:
        try:
            btn_data = list(filter(lambda i: callback_data.id == i.id, button_data))
            button_name = f"{btn_data[0].place_name} {btn_data[0].address}"
            button = InlineKeyboardButton(
                text=button_name, callback_data=callback_data.pack()
            )
            return button
        except ValueError:
            raise


    @staticmethod
    def __place_button(
            callback_data: PlacesEditorFactory,
            button_data: list[PlacesSchema]
    ) -> InlineKeyboardButton:
        try:
            btn_data = list(filter(lambda i: callback_data.id == i.id, button_data))
            button_name = f"{btn_data[0].place_name} -- {btn_data[0].address}"
            button = InlineKeyboardButton(
                text=button_name, callback_data=callback_data.pack()
            )
            return button
        except ValueError:
            raise
