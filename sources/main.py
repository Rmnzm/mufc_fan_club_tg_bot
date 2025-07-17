import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config.config import get_settings
from services.match_invitor_service import MatchInvitorManager
from functions.season_matches_manager import SeasonMatchesManager
from handlers import main_handler
from handlers.admin import base_admin_handler
from handlers.admin import create_place_handler
from handlers.admin import edit_place_handler
from handlers.admin import watch_day_edition_handler
from handlers.admin import watch_day_handler
from handlers.customer import meeting_approvement_handler
from handlers.customer import watch_day_registration_handler

settings = get_settings()

logger = logging.getLogger(__name__)

redis = Redis(host="localhost")
redis_storage = RedisStorage(redis=redis)

season_manager = SeasonMatchesManager()


async def create_or_update_matches_task():
    logger.info("Create/update next matches task is starting ...")
    await asyncio.sleep(15)
    while True:
        logger.info("Create/update next matches task is running ...")
        try:
            matches = season_manager.get_next_matches()
            if matches:
                season_manager.update_next_matches(matches)
                logger.info("Matches updated")
            else:
                logger.info("No matches to update")
        except Exception as e:
            logger.error(f"Error in create/update matches task: {e}")
        await asyncio.sleep(int(settings.update_match_job_timeout_in_sec))


async def send_invites_task(redis_client: Redis, bot_client: Bot):
    while True:
        logger.info("Checking status to send invitations  ...")
        try:
            await MatchInvitorManager(redis=redis_client, bot=bot_client).send()
        except Exception as e:
            logger.error(f"Error in send invites task: {e}")
        await asyncio.sleep(int(settings.send_job_timeout_in_sec))


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] #%(levelname)-8s %(filename)s:"
        "%(lineno)d - %(name)s - %(message)s",
    )

    logger.info("Starting bot...")

    bot = Bot(
        token=settings.tg_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dispatcher = Dispatcher(storage=redis_storage)

    dispatcher.include_router(main_handler.router)
    dispatcher.include_router(base_admin_handler.router)
    dispatcher.include_router(watch_day_handler.router)
    dispatcher.include_router(watch_day_registration_handler.router)
    dispatcher.include_router(watch_day_edition_handler.router)
    dispatcher.include_router(create_place_handler.router)
    dispatcher.include_router(edit_place_handler.router)
    dispatcher.include_router(meeting_approvement_handler.router)

    # create_or_update_matches_job = asyncio.create_task(create_or_update_matches_task())
    send_inviters_job = asyncio.create_task(
        send_invites_task(redis_client=redis, bot_client=bot)
    )

    try:
        logger.info("Bot started.")
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(bot)
    finally:
        # create_or_update_matches_job.cancel()
        send_inviters_job.cancel()


asyncio.run(main())
