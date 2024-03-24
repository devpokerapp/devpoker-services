from sqlalchemy import Column, String, Uuid, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from base.models import Model


class Invite(Model):
    __tablename__ = "invites"

    code = Column(
        String(),
        nullable=False
    )

    expires_at = Column(
        DateTime,
        nullable=False
    )

    poker_id = Column(
        Uuid(),
        ForeignKey("pokers.id", name="fk_invites_poker_id"),
        nullable=False
    )

    poker = relationship("Poker", back_populates="invites")
