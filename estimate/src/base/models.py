import datetime

from sqlalchemy import Column, DateTime, Uuid
from sqlalchemy.ext.declarative import declarative_base


class Base(object):
    id = Column(
        Uuid,
        nullable=False
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
