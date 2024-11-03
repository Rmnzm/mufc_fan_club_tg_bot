from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.BASE_LEXICON_RU import BASE_LEXICON_RU


class MainKeyboard:

    @staticmethod
    def main_keyboard():
        add_match_day = InlineKeyboardButton(
            text=BASE_LEXICON_RU["add_match_day"], callback_data="add_match_day"
        )
        scheduled_match_days = InlineKeyboardButton(
            text=BASE_LEXICON_RU["scheduled_match_days"], callback_data="scheduled_match_days"
        )

        main_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [add_match_day],
                [scheduled_match_days]
            ],
            resize_keyboard=True,
        )

        return main_keyboard
