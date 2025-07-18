import logging
from aiogram import Bot
from redis.asyncio import Redis

from datetime import datetime, timezone, timedelta
from config.config import get_settings
from functions.meeting_invites_manager import MeetingInvitesManager
from functions.season_matches_manager import SeasonMatchesManager
from aiogram.fsm.context import FSMContext, StorageKey
from aiogram.fsm.storage.redis import RedisStorage


settings = get_settings()

logger = logging.getLogger(__name__)

season_manager = SeasonMatchesManager()


class MatchInvitorManager:

    def __init__(self, redis: Redis, bot: Bot):
        self.redis = RedisStorage(redis=redis)
        self.bot = bot

    async def send(self):
        users, match_day_context = await season_manager.create_context_to_send_invitations()
        if not match_day_context:
            logger.info("No matches to send invitations. Skipping ...")
            return
        is_time_so_send = self.__is_time_to_send(match_day_context.get("meeting_date"))

        if users and is_time_so_send:
            for user in users:
                if user:
                    logging.info(f"Sending invitation to user {user.user_id}")
                    state = FSMContext(
                        storage=self.redis,
                        key=StorageKey(
                            user_id=user.user_id,
                            bot_id=int(settings.tg_bot_id),
                            chat_id=user.user_id,
                        ),
                    )
                    await MeetingInvitesManager(self.bot).send_message(
                        state=state, context=match_day_context, user_id=user.user_id
                    )
                    await season_manager.update_message_sent_status(
                        match_day_context, user.user_id
                    )

    @staticmethod
    def __is_time_to_send(match_day_time: datetime = None):
        if not match_day_time:
            logger.info("Match day time not found or match_day is not exists")
            return False
        
        match_day_datetime = datetime.strptime(match_day_time, "%a, %d %b %H:%M")
        if match_day_datetime.tzinfo is None:
            match_day_datetime = match_day_datetime.replace(
                tzinfo=timezone.utc
            ) + timedelta(hours=3)
        current_time = datetime.now(timezone.utc) + timedelta(hours=3)
        logger.info(
            f"Checking current time current_time={current_time.strftime('%a, %d %b %H:%M')} "
        )
        meeting_timedelta = match_day_datetime - current_time + timedelta(hours=4)
        meeting_delta_hours = meeting_timedelta.total_seconds() // 3600

        if meeting_delta_hours <= int(settings.timedelta_to_start_sending_in_hours):
            logger.info("It's time to send. Sending ...")
            return True

        logger.info(
            f"It's not time to send. Before next meeting {meeting_delta_hours} hours"
        )
