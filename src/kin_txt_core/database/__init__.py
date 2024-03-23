from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from .driver import Database
from .async_driver import AsyncDatabase

metadata = MetaData()


class Base(DeclarativeBase):
    pass
