import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext, StorageKey

from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config.config import get_settings
from functions.meeting_invites_manager import MeetingInvitesManager
from functions.season_matches_manager import SeasonMatchesManager
from handlers import main_handler, poll_task_handler
from handlers.admin import base_admin_handler
from handlers.customer import watch_day_registration_handler
from handlers.admin import watch_day_edition_handler
from handlers.admin import create_place_handler
from handlers.admin import watch_day_handler
from handlers.admin import edit_place_handler

settings = get_settings()

logger = logging.getLogger(__name__)

redis = Redis(host='localhost')

print(f"Redis here - {redis}")

redis_storage = RedisStorage(redis=redis)
season_manager = SeasonMatchesManager()


async def create_or_update_matches_task():
    while True:
        logger.info("Выполняется задача обновления/добавления будущих матчей...")
        try:
            update_test = SeasonMatchesManager().get_next_matches()
            SeasonMatchesManager().update_next_matches(update_test)
        except Exception as e:
            logger.error(e)
        await asyncio.sleep(3600)

async def update_last_passed_match_task():
    while True:
        logger.info("Выполняется задача обновления прошедших матчей")
        try:
            update_test = SeasonMatchesManager().get_nearest_events()
            SeasonMatchesManager().update_last_passed_match(update_test)
        except Exception as e:
            logger.error(e)
        await asyncio.sleep(3600)


async def send_invites(bot):
    while True:
        logger.info("Отправляется сообщение пользователю: ...")
        try:
            user_id = 715078441
            state = FSMContext(storage=redis_storage, key=StorageKey(user_id=user_id, bot_id=5182705497, chat_id=user_id))
            await MeetingInvitesManager(bot).send_message(state=state, context={"a": "b"})
        except Exception as e:
            logger.error(e)
        await asyncio.sleep(360)


async def main():
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
                               '%(lineno)d - %(name)s - %(message)s')

    logger.info("Starting bot...")

    # TODO: Сделать таску, которая добавляет/обновляет матчи, запрашивая их по апи

    bot = Bot(token=settings.tg_token,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dispatcher = Dispatcher(storage=redis_storage)

    dispatcher.include_router(main_handler.router)
    dispatcher.include_router(base_admin_handler.router)
    dispatcher.include_router(watch_day_handler.router)
    dispatcher.include_router(watch_day_registration_handler.router)
    dispatcher.include_router(watch_day_edition_handler.router)
    dispatcher.include_router(create_place_handler.router)
    dispatcher.include_router(edit_place_handler.router)

    # create_or_update_matches_job = asyncio.create_task(create_or_update_matches_task())
    # update_last_passed_match_job = asyncio.create_task(update_last_passed_match_task())
    send_inviters_job = asyncio.create_task(send_invites(bot=bot))

    logger.info("Bot started.")

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)

    # await create_or_update_matches_job
    # await update_last_passed_match_job
    await send_inviters_job


asyncio.run(main())
