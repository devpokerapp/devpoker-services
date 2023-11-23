from sqlalchemy import Column, String, Uuid, ForeignKey
from sqlalchemy.orm import relationship
from base.models import Model


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

    # TODO: participant connection status

    poker = relationship("Poker", back_populates="participants")
