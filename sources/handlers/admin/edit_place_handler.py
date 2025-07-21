import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from callback_factory.callback_factory import PlacesEditorFactory
from functions.admin_checker import AdminFilter
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.admin_keyboard import AdminKeyboard
from keyboards.keyboard_generator import KeyboardGenerator
from lexicon.admin_lexicon_ru import BASE_ADMIN_LEXICON_RU, ERROR_ADMIN_LEXICON_RU

logger = logging.getLogger(__name__)

router = Router()

match_day_manager = KznRedsPGManager()

admin_keyboard = AdminKeyboard()
keyboard_generator = KeyboardGenerator()


class PlaceState(StatesGroup):
    place_id = State()
    delete_place = State()
    edit_name = State()
    edit_address = State()
    approve_changes = State()


@router.callback_query(PlacesEditorFactory.filter(), AdminFilter())
async def edit_place_process(
    callback: CallbackQuery, callback_data: PlacesEditorFactory, state: FSMContext
):
    try:
        logger.debug(f"Step edit_place_process with callback_data={callback_data}")
        place_id = callback_data.id
        await state.set_state(PlaceState.place_id)
        await state.update_data(place_id=place_id)

        await callback.message.edit_text(
            text=BASE_ADMIN_LEXICON_RU["edit_place_process"],
            reply_markup=admin_keyboard.edit_place_keyboard(name=True, address=True),
        )
    except Exception as error:
        logger.error(f"Failed to process edit_place_process command. Err: {error}")
        await callback.message.edit_text(
            text=ERROR_ADMIN_LEXICON_RU["failed_edit_place_process"],
            reply_markup=admin_keyboard.main_admin_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data == "edit_name", AdminFilter())
async def edit_place_name_process(callback: CallbackQuery, state: FSMContext):
    try:
        logger.debug(f"Step edit_place_name_process with context = {callback.data}")
        await state.set_state(PlaceState.edit_name)
        await callback.message.answer(
            text=BASE_ADMIN_LEXICON_RU["edit_place_name_process"]
        )
    except Exception as error:
        logger.error(f"Failed to start editing place name. Err: {error}")
        await callback.message.edit_text(
            text=ERROR_ADMIN_LEXICON_RU["failed_edit_place_name_process"],
            reply_markup=admin_keyboard.main_admin_keyboard(),
        )
    await callback.answer()


@router.message(PlaceState.edit_name, AdminFilter())
async def edit_place_name(message: Message, state: FSMContext):
    place_state_data = await state.get_data()
    place_id = place_state_data["place_id"]
    new_place_name = message.text

    try:
        logger.debug(
            f"Step edit_place_name with context: {message.text} from user {message.from_user.id}"
        )
        old_place_name = await match_day_manager.change_place_name(
            place_id=place_id, new_place_name=new_place_name
        )
        await message.answer(
            text=BASE_ADMIN_LEXICON_RU["edit_place_name"].format(
                old_place_name=old_place_name,
                new_place_name=new_place_name
            ),
            reply_markup=admin_keyboard.edit_place_keyboard(address=True),
        )
    except Exception as error:
        logger.error(f"Failed to process editing place name. Err: {error}")
        await message.answer(
            text=ERROR_ADMIN_LEXICON_RU["failed_edit_place_name"],
            reply_markup=admin_keyboard.main_admin_keyboard(),
        )
    await state.clear()


@router.callback_query(F.data == "edit_address", AdminFilter())
async def edit_address_place_process(callback: CallbackQuery, state: FSMContext):
    try:
        logger.debug(
            f"Step edit_place_name with context: {callback.data} from user {callback.from_user.id}"
        )
        await state.set_state(PlaceState.edit_address)
        await callback.message.answer(
            text=BASE_ADMIN_LEXICON_RU["edit_address_place_process"]
        )
    except Exception as error:
        logger.error(f"Failed to start editing place address process. Err: {error}")
        await callback.message.answer(
            text=ERROR_ADMIN_LEXICON_RU["failed_edit_address_place_process"],
            reply_markup=admin_keyboard.main_admin_keyboard(),
        )
    await callback.answer()


@router.message(PlaceState.edit_address, AdminFilter())
async def edit_place_address(message: Message, state: FSMContext):
    place_state_data = await state.get_data()
    place_id = place_state_data["place_id"]
    new_place_address = message.text

    try:
        logger.debug(
            f"Step edit_place_name with context: {message.text} from user {message.from_user.id}"
        )
        await match_day_manager.change_place_address(
            place_id=place_id, new_place_address=new_place_address
        )
        await message.answer(
            text=BASE_ADMIN_LEXICON_RU["edit_place_address"].format(
                new_place_address=new_place_address
            ),
            reply_markup=admin_keyboard.edit_place_keyboard(name=True),
        )
    except Exception as error:
        logger.error(f"Failed to update place address. Err: {error}")
        await message.answer(
            text=ERROR_ADMIN_LEXICON_RU["failed_edit_place_address"],
            reply_markup=admin_keyboard.main_admin_keyboard(),
        )


@router.callback_query(F.data == "delete_place", AdminFilter())
async def delete_place(callback: CallbackQuery, state: FSMContext):
    place_state_data = await state.get_data()
    place_id = place_state_data["place_id"]

    try:
        logger.debug(
            f"Step edit_place_name with context: {callback.data} from user {callback.from_user.id}"
        )

        place_name = await match_day_manager.delete_place(place_id=place_id)
        await callback.message.answer(
            text=BASE_ADMIN_LEXICON_RU["delete_place"].format(
                place_name=place_name
            ),
            reply_markup=admin_keyboard.main_admin_keyboard(),
        )

    except Exception as error:
        logger.error(f"Failed to delete place. Err: {error}")
        await callback.message.edit_text(
            text=ERROR_ADMIN_LEXICON_RU["failed_delete_place"],
            reply_markup=admin_keyboard.main_admin_keyboard(),
        )
    await state.clear()
    await callback.answer()
