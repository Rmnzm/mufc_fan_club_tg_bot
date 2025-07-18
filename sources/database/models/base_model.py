import logging
import peewee
import peewee_async
from config.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Инициализация базы данных
pg_db = peewee_async.PostgresqlDatabase(
    database=settings.database,
    user=settings.login,
    password=settings.password,
    host=settings.host,
    port=settings.port,
)

# Менеджер асинхронных операций
objects = peewee_async.Manager(pg_db)
pg_db.set_allow_sync(False)

class BaseModel(peewee.Model):
    class Meta:
        database = pg_db
