import datetime
import uuid

from sqlalchemy import Column, DateTime, Uuid
from sqlalchemy.orm import declarative_base


class Base(object):
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


DeclarativeBase = declarative_base(cls=Base)
