import datetime

from sqlalchemy import Column, Text, Integer, text
from sqlalchemy.orm import declared_attr, declarative_base

from fastapi_template.app.util.snowflake import SnowflakeGenerator
from fastapi_template.config import settings

Base = declarative_base()
gen = SnowflakeGenerator(settings.SNOWFLAKE_INSTANCE)


class BaseSQLModel(Base):
    __abstract__ = True

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__

    id = Column(Integer, primary_key=True, default=gen.__next__)
    create_time = Column(Text, nullable=False, default="")
    update_time = Column(Text, nullable=False, default=datetime.datetime.utcnow())
    create_by = Column(Text, nullable=False, default="system")
    update_by = Column(Text, nullable=False, default="system")
    is_active = Column(Integer, nullable=False, server_default=text('1'))

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
