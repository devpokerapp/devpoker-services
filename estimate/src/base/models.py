import datetime
import uuid

from sqlalchemy import Column, DateTime, Uuid
from sqlalchemy.orm import declarative_base

DeclarativeBase = declarative_base()


class Model(DeclarativeBase):
    __abstract__ = True

    id = Column(
        Uuid,
        nullable=False,
        primary_key=True,
        default=uuid.uuid4
    )
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )

    def to_dict(self) -> dict:
        return self.__dict__
