import logging
import peewee
import peewee_async
from config.config import get_settings
from peewee_async import Manager, PostgresqlDatabase

settings = get_settings()
logger = logging.getLogger(__name__)

pg_db = PostgresqlDatabase(
    database=settings.database,
    user=settings.login,
    password=settings.password,
    host=settings.host,
    port=settings.port,
)

objects = Manager(pg_db)
pg_db.set_allow_sync(False)

class BaseModel(peewee.Model):
    class Meta:
        database = pg_db
