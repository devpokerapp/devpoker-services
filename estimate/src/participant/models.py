from sqlalchemy import Column, String, Uuid, ForeignKey
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
