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

    keycloak_user_id = Column(
        String(),
        nullable=True
    )

    poker_id = Column(
        Uuid(),
        ForeignKey("pokers.id", name="participants_poker_id"),
        nullable=False
    )

    # TODO: participant connection status

    poker = relationship("Poker", back_populates="participants")
    votes = relationship("Vote", back_populates="participant")
