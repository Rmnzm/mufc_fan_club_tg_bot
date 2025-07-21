import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config.config import get_settings
from functions.admin_checker import AdminFilter
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.admin_keyboard import AdminKeyboard
from lexicon.admin_lexicon_ru import BASE_ADMIN_LEXICON_RU, ERROR_ADMIN_LEXICON_RU
from states.create_place_state import CreatePlaceStateGroup

logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()
match_day_manager = KznRedsPGManager()
admin_keyboard = AdminKeyboard()


@router.message(CreatePlaceStateGroup.start_state, AdminFilter())
async def input_place_name(message: Message, state: FSMContext):
    logger.debug(f"Step inputting place name")
    try:
        await state.set_state(CreatePlaceStateGroup.add_place_state)
        await state.set_data(dict(add_place_state=message.text))

        await message.answer(
            text=BASE_ADMIN_LEXICON_RU["add_watching_place_step_2"].format(
                place_name=message.text
            )
        )
        logger.info(
            f"Successfully processed place name with context={message.text} from user={message.from_user.id}"
        )
    except Exception as e:
        logger.error(
            f"Failed to process place name inputting context={message.text} from user={message.from_user.id}. Err: {e}"
        )
        await message.answer(text=ERROR_ADMIN_LEXICON_RU["error_input_place_name"])


@router.message(CreatePlaceStateGroup.add_place_state, AdminFilter())
async def input_place_address(message: Message, state: FSMContext):
    logger.debug(f"Step inputting place address")
    current_state_data = await state.get_data()
    await state.set_data(dict(add_address_state=message.text))

    try:
        await match_day_manager.add_watch_place(
            place_name=current_state_data["add_place_state"], place_address=message.text
        )

        await message.answer(
            text=BASE_ADMIN_LEXICON_RU["add_watching_place_step_final"].format(
                place_name=current_state_data["add_place_state"],
                place_address=message.text,
            ), 
            reply_markup=admin_keyboard.main_admin_keyboard()
        )
        logger.info(
            f"Successfully processed place address with context={current_state_data}"
        )
    except Exception as e:
        logger.error(
            f"Failed to process place address inputting context={current_state_data}. Err: {e}"
        )
        await message.answer(text=ERROR_ADMIN_LEXICON_RU["error_input_place_address"])
    await state.clear()
