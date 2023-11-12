from sqlalchemy import Column, String, Uuid, ForeignKey
from sqlalchemy.orm import relationship
from base.models import Model
from poker.models import Poker


class Participant(Model):
    __tablename__ = "participants"

    name = Column(
        String(),
        nullable=False
    )

    sid = Column(
        String(),
        nullable=False
    )

    poker_id = Column(
        Uuid(),
        ForeignKey("pokers.id", name="fk_stories_poker_id"),
        nullable=False
    )

    poker = relationship(Poker, backref="stories")
