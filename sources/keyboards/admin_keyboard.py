from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.button_lexicon_ru import (
    ADMIN_KEYBOARD_BUTTON_LEXICON_RU,
    ADMIN_PLACE_KEYBOARD_BUTTON_LEXICON_RU,
    ADMIN_WATCH_DAY_KEYBOARD_BUTTON_LEXICON_RU,
)


class AdminKeyboard:

    @staticmethod
    def main_admin_keyboard():
        show_users = InlineKeyboardButton(
            text=ADMIN_KEYBOARD_BUTTON_LEXICON_RU["fan_list"],
            callback_data="show_users",
        )
        show_nearest_watching_days = InlineKeyboardButton(
            text=ADMIN_KEYBOARD_BUTTON_LEXICON_RU["nearest_meetings"],
            callback_data="show_nearest_watching_days",
        )
        show_places = InlineKeyboardButton(
            text=ADMIN_KEYBOARD_BUTTON_LEXICON_RU["places"], callback_data="show_places"
        )
        add_watching_place = InlineKeyboardButton(
            text=ADMIN_KEYBOARD_BUTTON_LEXICON_RU["add_place"],
            callback_data="add_watching_place",
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [show_users],
                [show_nearest_watching_days],
                [show_places],
                [add_watching_place],
            ],
            resize_keyboard=True,
        )
        return keyboard

    @staticmethod
    def edit_meeting_keyboard():
        edit_place = InlineKeyboardButton(
            text=ADMIN_WATCH_DAY_KEYBOARD_BUTTON_LEXICON_RU["edit_watch_place"],
            callback_data="edit_watch_place",
        )
        cancel_meeting = InlineKeyboardButton(
            text=ADMIN_WATCH_DAY_KEYBOARD_BUTTON_LEXICON_RU["cancel_meeting"],
            callback_data="cancel_meeting",
        )
        show_visitors = InlineKeyboardButton(
            text=ADMIN_WATCH_DAY_KEYBOARD_BUTTON_LEXICON_RU["show_visitors"],
            callback_data="show_visitors",
        )
        start_meeting_poll = InlineKeyboardButton(
            text=ADMIN_WATCH_DAY_KEYBOARD_BUTTON_LEXICON_RU["start_meeting_poll"],
            callback_data="start_meeting_poll",
        )
        back_to_main_menu = InlineKeyboardButton(
            text=ADMIN_WATCH_DAY_KEYBOARD_BUTTON_LEXICON_RU["back_to_main_menu"],
            callback_data="back_to_main_menu",
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [start_meeting_poll],
                [edit_place, cancel_meeting],
                [show_visitors],
                [back_to_main_menu],
            ],
            resize_keyboard=True,
        )

        return keyboard

    @staticmethod
    def edit_place_keyboard(name=False, address=False):
        edit_name = InlineKeyboardButton(
            text=ADMIN_PLACE_KEYBOARD_BUTTON_LEXICON_RU["edit_name"],
            callback_data="edit_name",
        )
        edit_address = InlineKeyboardButton(
            text=ADMIN_PLACE_KEYBOARD_BUTTON_LEXICON_RU["edit_address"],
            callback_data="edit_address",
        )
        delete_place = InlineKeyboardButton(
            text=ADMIN_PLACE_KEYBOARD_BUTTON_LEXICON_RU["delete_place"],
            callback_data="delete_place",
        )
        back_to_main_menu = InlineKeyboardButton(
            text=ADMIN_PLACE_KEYBOARD_BUTTON_LEXICON_RU["back_to_main_menu"],
            callback_data="back_to_main_menu",
        )
        buttons = []
        if name:
            buttons.append(edit_name)
        if address:
            buttons.append(edit_address)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [delete_place],
                buttons,
                [back_to_main_menu],
            ],
            resize_keyboard=True,
        )

        return keyboard
