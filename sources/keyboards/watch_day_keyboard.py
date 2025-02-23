from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.watch_day_lexicon_ru import WATCH_DAY_LEXICON_RU


class WatchDayKeyboard:

    @staticmethod
    def watch_day_keyboard():
        add_watch_day = InlineKeyboardButton(
            text=WATCH_DAY_LEXICON_RU["add_watch_day"], callback_data="add_watch_day"
        )
        choose_another_match_day = InlineKeyboardButton(
            text=WATCH_DAY_LEXICON_RU["choose_another_match_day"], callback_data="choose_another_match_day"
        )
        cancel_adding = InlineKeyboardButton(
            text=WATCH_DAY_LEXICON_RU["cancel_adding"], callback_data="cancel_adding"
        )
        main_menu = InlineKeyboardButton(
            text=WATCH_DAY_LEXICON_RU["main_menu"], callback_data="main_menu"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [add_watch_day],
                [choose_another_match_day],
                [cancel_adding, main_menu],
            ],
            resize_keyboard=True,
        )

        return keyboard

    @staticmethod
    def approve_meeting_keyboard():
        go_button = InlineKeyboardButton(
            text="Иду", callback_data="go_button"
        )
        not_go_button = InlineKeyboardButton(
            text="Не иду", callback_data="not_go_button"
        )
        menu_button = InlineKeyboardButton(
            text="Назад в меню", callback_data="menu_button"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [go_button, not_go_button],
                [menu_button],
            ],
            resize_keyboard=True,
        )

        return keyboard
