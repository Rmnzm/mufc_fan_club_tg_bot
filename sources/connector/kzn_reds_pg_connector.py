import logging

import psycopg2
from psycopg2 import InterfaceError, OperationalError
from psycopg2._psycopg import connection

from tools.singleton import SingletonWithParams
from config.config import get_settings


settings = get_settings()

logger = logging.getLogger(__name__)


class KznRedsPgConnector(metaclass=SingletonWithParams):
    def __init__(self):
        self.instance_connection = None

    @property
    def connection(self) -> connection:
        if (
            not self.instance_connection
            or self.instance_connection.closed
            or not self.is_connection_valid
        ):
            try:
                self.instance_connection = psycopg2.connect(
                    dbname=settings.database,
                    user=settings.login,
                    password=settings.password,
                    host=settings.host,
                    port=settings.port,
                )
                self.instance_connection.autocommit = False
            except Exception as error:
                raise RuntimeError("Connection to PG KZN_REDS failed") from error

        return self.instance_connection

    @property
    def is_connection_valid(self):
        try:
            with self.instance_connection.cursor() as active_cursor:
                active_cursor.execute("SELECT 1")
        except (InterfaceError, OperationalError) as interface_error:
            self.instance_connection.close()
            logger.warning(
                f"Connection to KZN_REDS will be reloaded, cause failed with error: {interface_error}"
            )
            return False
        except Exception as error:
            self.instance_connection.close()
            logger.exception(f"Error when trying to ping PSQL connection: {error}")
            return False
        return True

    def __del__(self):
        if not self.instance_connection.closed:
            self.instance_connection.close()

    def execute_command(self, command: str, debug_log: str, exception_log: str):
        with self.connection as active_connection:
            try:
                with active_connection.cursor() as active_cursor:
                    active_cursor.execute(command)
                    active_connection.commit()
                    logger.debug(lambda: f"Step execute_command with {debug_log}")
            except Exception as error:
                active_connection.rollback()
                logger.exception(f"{exception_log}, Error: {error}")
                raise

    def select_with_dict_result(self, command):
        with self.connection as active_connection:
            with active_connection.cursor() as active_cursor:
                active_cursor.execute(command)
                columns = [col[0].lower() for col in active_cursor.description]
                rows = active_cursor.fetchall()
        rows_as_dicts = [dict(zip(columns, row)) for row in rows]
        return rows_as_dicts
