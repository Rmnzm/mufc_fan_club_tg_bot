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
            text="Изменить место", callback_data="edit_watch_place"
        )
        cancel_meeting = InlineKeyboardButton(
            text="Отменить встречу", callback_data="cancel_meeting"
        )
        show_visitors = InlineKeyboardButton(
            text="Показать учатсников", callback_data="show_visitors"
        )
        start_meeting_poll = InlineKeyboardButton(
            text="Запустить предварительный опрос", callback_data="start_meeting_poll"
        )
        back_to_main_menu = InlineKeyboardButton(
            text="Назад в меню", callback_data="back_to_main_menu"
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
            text="Изменить название", callback_data="edit_name"
        )
        edit_address = InlineKeyboardButton(
            text="Изменить адрес", callback_data="edit_address"
        )
        delete_place = InlineKeyboardButton(
            text="Удалить", callback_data="delete_place"
        )
        back_to_main_menu = InlineKeyboardButton(
            text="Назад в меню", callback_data="back_to_main_menu"
        )
        btns = []
        if name:
            btns.append(edit_name)
        if address:
            btns.append(edit_address)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [delete_place],
                btns,
                [back_to_main_menu],
            ],
            resize_keyboard=True,
        )

        return keyboard
