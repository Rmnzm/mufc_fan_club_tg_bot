from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.WATCH_DAY_LEXICON_RU import WATCH_DAY_LEXICON_RU


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
