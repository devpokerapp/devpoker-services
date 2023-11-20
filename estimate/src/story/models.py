from sqlalchemy import Column, String, Uuid, ForeignKey
from sqlalchemy.orm import relationship

from base.models import Model


class Story(Model):
    __tablename__ = "stories"

    name = Column(
        String(),
        nullable=False
    )

    description = Column(
        String(),
        nullable=True
    )

    value = Column(
        String(),
        nullable=True
    )

    poker_id = Column(
        Uuid(),
        ForeignKey("pokers.id", name="fk_stories_poker_id"),
        nullable=False
    )

    events = relationship("Event", back_populates="story")
