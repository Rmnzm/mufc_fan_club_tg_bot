import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, Poll, PollAnswer, PollOption

from config.config import get_settings
from functions.kzn_reds_pg_manager import KznRedsPGManager
from keyboards.keyboard_generator import KeyboardGenerator
from keyboards.main_keyboard import MainKeyboard
from keyboards.watch_day_keyboard import WatchDayKeyboard

logger = logging.getLogger(__name__)

settings = get_settings()

router = Router()
main_keyboard = MainKeyboard()
watch_day_keyboard = WatchDayKeyboard()
keyboard_generator = KeyboardGenerator()

match_day_manager = KznRedsPGManager()


@router.message(Command(commands=['poll']))
async def poll_task_creator(message: Message):
    question = "Какой ваш любимый язык программирования?"
    options = [
        PollOption(text="Python", voter_count=0),
        PollOption(text="Java", voter_count=0)
    ]

    poll = Poll(
        id="1",
        question=question,
        options=options,
        is_anonymous=False,
        type='regular',
        allows_multiple_answers=False,
        total_voter_count=0,
        is_closed=True
    )

    await message.answer_poll(
        question=poll.question, options=["Python", "Java"]
    )

@router.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer):
    user_id = poll_answer.user.id
    poll_id = poll_answer.poll_id
    option_ids = ','.join(map(str, poll_answer.option_ids))

    print(f"User {user_id} voted in poll {poll_id} with options {option_ids}")
