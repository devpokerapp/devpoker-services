from sqlalchemy import Column, String, Uuid, ForeignKey
from sqlalchemy.orm import relationship
from base.models import Model


class Poker(Model):
    __tablename__ = "pokers"

    creator = Column(
        String(),
        nullable=False
    )

    vote_pattern = Column(String(), nullable=False, server_default="0,1,2,3,5,8,13,?,__coffee")

    current_story_id = Column(
        Uuid(),
        # FIXME: foreign key causing circular import
        # ForeignKey("stories.id", name="fk_pokers_current_story_id"),
        nullable=True
    )

    # TODO: current_story
    stories = relationship("Story", back_populates="poker")
    participants = relationship("Participant", back_populates="poker")
    invites = relationship("Invite", back_populates="poker")
