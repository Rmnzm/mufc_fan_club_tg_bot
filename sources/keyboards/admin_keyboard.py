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
        add_watching_place = InlineKeyboardButton(
            text="Добавить место просмотра", callback_data="add_watching_place"
        )
        # back_to_main_menu = InlineKeyboardButton(
        #     text="Назад", callback_data="back_to_main_menu"
        # )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [show_users],
                [show_nearest_watching_days],
                [show_places],
                [add_watching_place]
                # [back_to_main_menu],
            ],
            resize_keyboard=True,
        )
        return keyboard


    @staticmethod
    def edit_meeting_keyboard():
        edit_place = InlineKeyboardButton(
            text="Изменить место", callback_data="edit_place"
        )
        cancel_meeting = InlineKeyboardButton(
            text="Отменить встречу", callback_data="cancel_meeting"
        )
        back_to_main_menu = InlineKeyboardButton(
            text="Назад в меню", callback_data="back_to_main_menu"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [edit_place, cancel_meeting],
                [back_to_main_menu],
            ],
            resize_keyboard=True,
        )

        return keyboard