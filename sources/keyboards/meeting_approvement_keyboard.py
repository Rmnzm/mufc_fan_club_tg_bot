from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class MeetingApprovementKeyboard:
    @staticmethod
    def main_approvement_keyboard():
        approve = InlineKeyboardButton(
            text="Да, буду", callback_data="approve_invitation"
        )
        cancel = InlineKeyboardButton(
            text="Нет, не смогу", callback_data="cancel_invitation"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [approve], [cancel]
            ],
            resize_keyboard=True
        )
        return keyboard