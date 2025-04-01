from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.base_lexicon_ru import BASE_LEXICON_RU


class MainKeyboard:

    @staticmethod
    def main_keyboard():
        nearest_meetings = InlineKeyboardButton(
            text=BASE_LEXICON_RU["nearest_meetings"], callback_data="nearest_meetings"
        )
        scheduled_match_days = InlineKeyboardButton(
            text=BASE_LEXICON_RU["scheduled_match_days"],
            callback_data="scheduled_match_days",
        )

        main_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [scheduled_match_days],
                [nearest_meetings],
            ],
            resize_keyboard=True,
        )

        return main_keyboard
