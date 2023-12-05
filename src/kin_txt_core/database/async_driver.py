from typing import Optional, Generator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker


class AsyncDatabase:
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
        self._session: Optional[AsyncSession] = None

    def _build_connection_string(self) -> str:
        return f"postgresql+asyncpg://{self._username}:{self._password}@{self._host}:{self._port}/{self._db_name}"

    def _create_engine(self) -> AsyncEngine:
        connection_string = self._build_connection_string()
        return create_async_engine(connection_string)

    @asynccontextmanager
    async def session(self) -> Generator[AsyncSession, None, None]:
        session = async_sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)

        async with session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
