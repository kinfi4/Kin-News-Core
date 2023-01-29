from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy.engine import Engine, Connection, create_engine
from sqlalchemy import MetaData

metadata = MetaData()


class Database:
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database_name: str,
    ) -> None:
        self._username = user
        self._host = host
        self._password = password
        self._port = port
        self._db_name = database_name

        self._engine = self._create_engine()
        self._connection: Optional[Connection] = None

    def _build_connection_string(self) -> str:
        return f'postgresql+psycopg2://{self._username}:{self._password}@{self._host}:{self._port}/{self._db_name}'

    def _create_engine(self) -> Engine:
        connection_string = self._build_connection_string()
        return create_engine(connection_string)

    @contextmanager
    def connection(self) -> Generator[Connection, None, None]:
        connection = self.get_db_connection()

        transaction = connection.begin()
        try:
            yield connection
            transaction.commit()
        except Exception:
            transaction.rollback()
            raise

    def get_db_connection(self) -> Connection:
        if self._connection is None:
            self._connection = self._engine.connect()

        return self._connection

    def close(self):
        self._connection.close()
