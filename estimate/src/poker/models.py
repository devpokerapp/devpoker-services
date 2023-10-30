from sqlalchemy import Column, String, Uuid, ForeignKey
from sqlalchemy.orm import relationship
from base.models import DeclarativeBase


class Poker(DeclarativeBase):
    __tablename__ = "pokers"

    creator = Column(
        String(),
        nullable=False
    )

    current_story_id = Column(
        Uuid(),
        # FIXME: foreign key causing circular import
        # ForeignKey("stories.id", name="fk_pokers_current_story_id"),
        nullable=True
    )
