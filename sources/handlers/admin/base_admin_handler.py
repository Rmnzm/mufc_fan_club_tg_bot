import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from callback_factory.callback_factory import (
    AdminMatchDayCallbackFactory,
    PlacesEditorFactory,
)
from functions.admin_checker import AdminFilter
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.admin_keyboard import AdminKeyboard
from keyboards.keyboard_generator import KeyboardGenerator
from keyboards.main_keyboard import MainKeyboard
from schemes.scheme import UsersSchema
from states.create_place_state import CreatePlaceStateGroup
from lexicon.admin_lexicon_ru import ADMIN_WATCH_DAY_HANDLER_LEXICON_RU, BASE_ADMIN_LEXICON_RU, ERROR_ADMIN_LEXICON_RU

logger = logging.getLogger(__name__)

router = Router()

match_day_manager = KznRedsPGManager()

main_keyboard = MainKeyboard()
admin_keyboard = AdminKeyboard()
keyboard_generator = KeyboardGenerator()


@router.message(Command(commands="admin"), AdminFilter())
async def process_admin_command(message: Message):
    await message.answer(
        text=BASE_ADMIN_LEXICON_RU["main_admin_menu"],
        reply_markup=admin_keyboard.main_admin_keyboard(),
    )


@router.callback_query(F.data == "show_users", AdminFilter())
async def show_users(callback: CallbackQuery):
    try:
        logger.debug(f"Step {F.data=}")
        users = match_day_manager.get_users()

        await callback.message.edit_text(
            text=__fetched_users(users),
            reply_markup=admin_keyboard.main_admin_keyboard(),
        )
    except Exception as e:
        logger.error(
            f"Error due reaction on {F.data=} with context {callback.data}. Err: {e}"
        )
        await callback.message.edit_text(
            text=ERROR_ADMIN_LEXICON_RU["error_show_users"],
            reply_markup=main_keyboard.main_keyboard(),
        )

    await callback.answer()


@router.callback_query(F.data == "show_nearest_watching_days", AdminFilter())
async def process_nearest_meetings(callback: CallbackQuery):
    try:
        logger.debug(f"Step {F.data=}")
        nearest_match_day_context = match_day_manager.get_nearest_meetings()
        data_factories = [
            AdminMatchDayCallbackFactory(id=context.match_day_id)
            for context in nearest_match_day_context
        ]
        reply_keyboard = keyboard_generator.admin_watch_day_keyboard(
            data_factories, nearest_match_day_context, add_watch_day=True
        )
        if nearest_match_day_context:
            await callback.message.edit_text(
                text=BASE_ADMIN_LEXICON_RU["show_nearest_watching_days"],
                reply_markup=reply_keyboard,
            )
        else:
            await callback.message.edit_text(
                text=ADMIN_WATCH_DAY_HANDLER_LEXICON_RU["no_nearest_matches"],
                reply_markup=admin_keyboard.main_admin_keyboard(),
            )
    except Exception as e:
        logger.error(
            f"Error due reaction on {F.data=} with context {callback.data}. Err: {e}"
        )
        await callback.message.edit_text(
            text=ERROR_ADMIN_LEXICON_RU["error_show_nearest_watching_days"],
            reply_markup=main_keyboard.main_keyboard(),
        )

    await callback.answer()


@router.callback_query(F.data == "add_watching_place", AdminFilter())
async def add_watching_place(callback: CallbackQuery, state: FSMContext):
    try:
        logger.debug(f"Step {F.data=}")
        await state.set_state(CreatePlaceStateGroup.start_state)
        await callback.message.edit_text(
            text=BASE_ADMIN_LEXICON_RU["add_watching_place"]
        )
    except Exception as e:
        logger.error(
            f"Error due reacting on {F.data=} with context {callback.data}. Err: {e}"
        )
        await callback.message.edit_text(
            text=ERROR_ADMIN_LEXICON_RU["error_adding_watching_place"],
            reply_markup=main_keyboard.main_keyboard(),
        )

    await callback.answer()


@router.callback_query(F.data == "show_places", AdminFilter())
async def show_places(callback: CallbackQuery):
    try:
        logger.debug(f"Step {F.data=}")
        places = match_day_manager.get_places()

        data_factories = [PlacesEditorFactory(id=context.id) for context in places]
        reply_keyboard = keyboard_generator.places_editor_keyboard(
            data_factories, places
        )

        await callback.message.edit_text(
            text=BASE_ADMIN_LEXICON_RU["fetched_places"], reply_markup=reply_keyboard
        )
    except Exception as e:
        logger.error(
            f"Error due reaction on {F.data=} with context {callback.data}. Err: {e}"
        )
        await callback.message.edit_text(
            text=ERROR_ADMIN_LEXICON_RU["error_show_places"],
            reply_markup=main_keyboard.main_keyboard(),
        )

    await callback.answer()


def __fetched_users(users: list[UsersSchema]) -> str:
    users_string = []

    for user in users:
        users_string.append(
            f"{user.first_name if user.first_name else ''} "
            f"{user.last_name if user.last_name else ''} -- "
            f"@{user.username} -- "
            f"{user.user_role}\n"
        )

    return "".join(users_string)
