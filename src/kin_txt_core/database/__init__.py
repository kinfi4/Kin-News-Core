from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

from .driver import Database
from .async_driver import AsyncDatabase

from kin_txt_core.settings import PostgresSettings

metadata = MetaData(schema=PostgresSettings().db_schema)
Base = declarative_base(metadata=metadata)
