import logging
from aiogram.types import Message, CallbackQuery

from aiogram import F, Router
from aiogram.filters import Command

from keyboards.admin_keyboard import AdminKeyboard

logger = logging.getLogger(__name__)

router = Router()

admin_keyboard = AdminKeyboard()


@router.message(Command(commands='admin'))
async def process_admin_command(message: Message):
    await message.answer(
        # TODO: rewrite message text
        text="Base admin command processing", reply_markup=admin_keyboard.main_admin_keyboard()
    )


@router.callback_query(F.data == "show_users")
async def show_users(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Тут будет список пользователей", reply_markup=admin_keyboard.main_admin_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data == "show_nearest_watching_days")
async def show_nearest_watching_days(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Тут будут кнопки с ближайшими просмотрами, клавиатура с кнопками"
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Base admin command processing", reply_markup=admin_keyboard.main_admin_keyboard()
    )
    await callback.answer()