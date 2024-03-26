from sqlalchemy import Column, String, Boolean, Uuid, ForeignKey
from sqlalchemy.orm import relationship, backref

from base.models import Model


class Vote(Model):
    __tablename__ = "votes"

    value = Column(
        String(),
        nullable=False
    )

    participant_id = Column(
        Uuid(),
        ForeignKey("participants.id", name="fk_votes_participant_id"),
        nullable=False
    )

    polling_id = Column(
        Uuid(),
        ForeignKey("pollings.id", name="fk_votes_polling_id", ondelete="CASCADE"),
        nullable=False
    )

    poker_id = Column(
        Uuid(),
        ForeignKey("pokers.id", name="fk_votes_poker_id"),
        nullable=False
    )

    participant = relationship("Participant", back_populates="votes")
    polling = relationship("Polling", backref=backref("votes", cascade="all, delete-orphan"))
