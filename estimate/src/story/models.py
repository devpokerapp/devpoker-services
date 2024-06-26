from sqlalchemy import Column, String, Uuid, ForeignKey, Integer, select, func, table
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

    order = Column(
        Integer(),
        nullable=False,
        default=select(func.count()).select_from(table('stories'))
    )

    poker_id = Column(
        Uuid(),
        ForeignKey("pokers.id", name="fk_stories_poker_id"),
        nullable=False
    )

    poker = relationship("Poker", back_populates="stories")
    events = relationship("Event", back_populates="story", order_by="Event.created_at")
