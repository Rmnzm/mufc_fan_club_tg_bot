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


def create_or_update_matches():
    logger.info("Create/update next matches task is starting ...")
    while True:
        logger.info("Create/update next matches task is running ...")
        try:
            matches = season_manager.get_next_matches()
            logger.info(f"Found {len(matches)} matches to update")
            if matches:
                batch_size = 10  # TODO: move to config
                for i in range(0, len(matches), batch_size):
                    chunk = matches[i:i + batch_size]
                    logger.debug(f"Processing batch {i//batch_size}: IDs {[m.eventId for m in chunk]}")
                    try:
                        season_manager.update_next_matches(chunk)
                    except Exception as e:
                        logger.error(f"Error processing batch {i//batch_size}: {e}")
                    logger.info(f"Batch {i//batch_size} processed successfully")
                logger.info("All matches processed!")
            else:
                logger.info("No matches to update")
        except Exception as e:
            logger.error(f"Error in create/update matches task: {e}")


async def send_invites_task(redis_client: Redis, bot_client: Bot):
    while True:
        logger.info("Checking status to send invitations  ...")
        try:
            await MatchInvitorManager(redis=redis_client, bot=bot_client).send()
        except Exception as e:
            logger.error(f"Error in send invites task: {e}")
        await asyncio.sleep(int(settings.send_job_timeout_in_sec))


async def main():
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
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot started.")
        await dispatcher.start_polling(bot)
    finally:
        # create_or_update_matches_job.cancel()
        send_inviters_job.cancel()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] #%(levelname)-8s %(filename)s:"
        "%(lineno)d - %(name)s - %(message)s",
    )

    create_or_update_matches()

    asyncio.run(main())
