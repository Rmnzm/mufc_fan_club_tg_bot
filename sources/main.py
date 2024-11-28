import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config.config import get_settings
from handlers import main_handler
from handlers.admin import watch_day_handler, add_match_day_handler

settings = get_settings()

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
                               '%(lineno)d - %(name)s - %(message)s')

    logger.info("Starting bot...")

    bot = Bot(token=settings.tg_token,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dispatcher = Dispatcher()

    dispatcher.include_router(main_handler.router)
    dispatcher.include_router(add_match_day_handler.router)
    dispatcher.include_router(watch_day_handler.router)

    logger.info("Bot started.")

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


asyncio.run(main())
