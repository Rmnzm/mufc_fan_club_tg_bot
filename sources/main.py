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
from handlers.customer import user_registration_handler

settings = get_settings()

logger = logging.getLogger(__name__)

# redis = Redis(host=settings.redis_host, port=settings.redis_port)
redis = Redis(host="localhost")
redis_storage = RedisStorage(redis=redis)

season_manager = SeasonMatchesManager()


async def create_or_update_matches():
    logger.info("Create/update next matches task is starting ...")
    while True:
        try:
            task = asyncio.create_task(_process_matches_update())
            await asyncio.wait_for(task, timeout=int(settings.default_task_timeout_in_sec))
            
        except asyncio.TimeoutError:
            logger.warning("Match update task timed out")
        except Exception as e:
            logger.error(f"Error in create/update matches task: {e}")
        finally:
            logger.info("Create/update next matches task is sleeping ...")
            await asyncio.sleep(int(settings.update_match_job_timeout_in_sec))

async def _process_matches_update():
    logger.info("Create/update next matches task is running ...")
    try:
        matches = await season_manager.get_next_matches()
        logger.info(f"Found {len(matches)} matches to update")
        
        if not matches:
            logger.info("No matches to update")
            return

        batch_size = int(settings.update_matches_default_batch_size)
        processed_matches = 0
        
        for i in range(0, len(matches), batch_size):
            chunk = matches[i:i + batch_size]
            logger.debug(f"Processing batch {len(chunk)} at index {i}: IDs {[m.eventId for m in chunk]}")
            
            try:
                await asyncio.sleep(0.1)
                await season_manager.update_next_matches(chunk)
                processed_matches += len(chunk)
            except Exception as e:
                logger.error(f"Error processing batch {len(chunk)} at index {i}: {e}")
            
            logger.info(f"Batch {i//batch_size} with {processed_matches=} processed successfully")
        
        logger.info("All matches processed!")
    except Exception as e:
        logger.error(f"Error in matches processing: {e}")
        raise


async def send_invites_task(redis_client: Redis, bot_client: Bot):
    while True:
        logger.info("Checking status to send invitations  ...")
        try:
            await MatchInvitorManager(redis=redis_client, bot=bot_client).send()
        except Exception as e:
            logger.error(f"Error in send invites task: {e}")
        await asyncio.sleep(int(settings.send_job_timeout_in_sec))


async def run_bot(bot: Bot):
    logger.info("Starting bot...")

    dispatcher = Dispatcher(storage=redis_storage)

    dispatcher.include_router(main_handler.router)
    dispatcher.include_router(base_admin_handler.router)
    dispatcher.include_router(user_registration_handler.router)
    dispatcher.include_router(watch_day_handler.router)
    dispatcher.include_router(watch_day_registration_handler.router)
    dispatcher.include_router(watch_day_edition_handler.router)
    dispatcher.include_router(create_place_handler.router)
    dispatcher.include_router(edit_place_handler.router)
    dispatcher.include_router(meeting_approvement_handler.router)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started.")
    await dispatcher.start_polling(bot)

async def main():
    bot = Bot(
        token=settings.tg_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await asyncio.gather(
        run_bot(bot=bot),
        create_or_update_matches(),
        send_invites_task(redis, bot_client=bot),
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s",
    )

    asyncio.run(main())
