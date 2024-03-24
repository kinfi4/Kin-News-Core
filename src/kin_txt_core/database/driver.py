import threading
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy.engine import Engine, Connection, create_engine
from sqlalchemy.orm import Session, sessionmaker, scoped_session


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
        self._connection_registry = threading.local()

        self._session_factory = sessionmaker(bind=self._create_engine(), expire_on_commit=False)

    def build_connection_string(self) -> str:
        return f"postgresql+psycopg2://{self._username}:{self._password}@{self._host}:{self._port}/{self._db_name}"

    def _create_engine(self) -> Engine:
        connection_string = self.build_connection_string()
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

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        _Session = scoped_session(self._session_factory)
        session = _Session()

        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            _Session.remove()

    def get_db_connection(self) -> Connection:
        try:
            return self._connection_registry.connection
        except AttributeError:
            self._connection_registry.connection = self._engine.connect()

        return self._connection_registry.connection

    def close(self) -> None:
        if self._connection_registry.connection is not None:
            self._connection_registry.connection.close()
