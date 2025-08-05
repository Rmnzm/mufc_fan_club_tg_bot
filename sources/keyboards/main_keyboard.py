from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.button_lexicon_ru import MAIN_KEYBOARD_BUTTON_LEXICON_RU


class MainKeyboard:

    @staticmethod
    def main_keyboard():
        scheduled_match_days = InlineKeyboardButton(
            text=MAIN_KEYBOARD_BUTTON_LEXICON_RU["scheduled_match_days"],
            callback_data="scheduled_match_days",
        )
        nearest_meetings = InlineKeyboardButton(
            text=MAIN_KEYBOARD_BUTTON_LEXICON_RU["nearest_meetings"],
            callback_data="nearest_meetings",
        )

        main_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [scheduled_match_days],
                [nearest_meetings],
            ],
            resize_keyboard=True,
        )

        return main_keyboard
