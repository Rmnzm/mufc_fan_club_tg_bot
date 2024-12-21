import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from callback_factory.callback_factory import AdminMatchDayCallbackFactory
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.admin_keyboard import AdminKeyboard
from keyboards.keyboard_generator import KeyboardGenerator
from states.create_place_state import CreatePlaceStateGroup

logger = logging.getLogger(__name__)

router = Router()

match_day_manager = KznRedsPGManager()

admin_keyboard = AdminKeyboard()
keyboard_generator = KeyboardGenerator()


@router.message(Command(commands='admin'))
async def process_admin_command(message: Message):
    await message.answer(
        # TODO: rewrite message text
        text="Base admin command processing", reply_markup=admin_keyboard.main_admin_keyboard()
    )


@router.callback_query(F.data == "show_users")
async def show_users(callback: CallbackQuery):
    users = match_day_manager.get_users()

    users_string = []

    for user in users:
        users_string.append(f"@{user.username} -- {user.user_role}\n")

    await callback.message.edit_text(
        text="".join(users_string), reply_markup=admin_keyboard.main_admin_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data == "show_nearest_watching_days")
async def process_nearest_meetings(callback: CallbackQuery):
    nearest_match_day_context = match_day_manager.get_nearest_meetings()
    data_factories = [
        AdminMatchDayCallbackFactory(
            id=context.id
        ) for context in nearest_match_day_context
    ]
    reply_keyboard = keyboard_generator.admin_watch_day_keyboard(
        data_factories, nearest_match_day_context, add_watch_day=True
    )
    await callback.message.edit_text(
        # TODO: add relevant text
        text="Some text",
        reply_markup=reply_keyboard
    )
    await callback.answer()



@router.callback_query(F.data == "add_watching_place")
async def add_watching_place(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreatePlaceStateGroup.start_state)
    await callback.message.edit_text(
        text="Добавление места"
    )
    await callback.answer()

