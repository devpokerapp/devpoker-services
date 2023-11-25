from sqlalchemy import Column, String, Boolean, Uuid, ForeignKey
from sqlalchemy.orm import relationship

from base.models import Model


class Vote(Model):
    __tablename__ = "votes"

    value = Column(
        String(),
        nullable=True
    )

    participant_id = Column(
        Uuid(),
        ForeignKey("participants.id", name="fk_votes_participant_id"),
        nullable=False
    )

    polling_id = Column(
        Uuid(),
        ForeignKey("pollings.id", name="fk_votes_polling_id"),
        nullable=False
    )
