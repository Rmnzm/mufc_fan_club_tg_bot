from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class AdminKeyboard:

    @staticmethod
    def main_admin_keyboard():
        # TODO: Переписать тексты кнопок
        show_users = InlineKeyboardButton(
            text="Пользователи", callback_data="show_users"
        )
        show_nearest_watching_days = InlineKeyboardButton(
            text="Ближайшие просмотры", callback_data="show_nearest_watching_days"
        )
        show_places = InlineKeyboardButton(
            text="Места просмотров", callback_data="show_places"
        )
        # back_to_main_menu = InlineKeyboardButton(
        #     text="Назад", callback_data="back_to_main_menu"
        # )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [show_users],
                [show_nearest_watching_days],
                [show_places],
                # [back_to_main_menu],
            ],
            resize_keyboard=True,
        )
        return keyboard