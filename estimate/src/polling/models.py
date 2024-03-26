from sqlalchemy import Column, String, Boolean, Uuid, ForeignKey
from sqlalchemy.orm import relationship, backref

from base.models import Model


class Polling(Model):
    __tablename__ = "pollings"

    value = Column(
        String(),
        nullable=True
    )

    completed = Column(
        Boolean(),
        nullable=False,
        default=False
    )

    revealed = Column(
        Boolean(),
        nullable=False,
        default=False
    )

    story_id = Column(
        Uuid(),
        ForeignKey("stories.id", name="fk_pollings_story_id", ondelete="CASCADE"),
        nullable=False
    )

    poker_id = Column(
        Uuid(),
        ForeignKey("pokers.id", name="fk_pollings_poker_id"),
        nullable=False
    )

    story = relationship("Story", backref=backref("pollings", cascade="all, delete-orphan", order_by='Polling.created_at'))
