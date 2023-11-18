from sqlalchemy import Column, String, Boolean, Uuid, ForeignKey

from base.models import Model


class Event(Model):
    __tablename__ = "events"

    type = Column(
        String(),
        nullable=False
    )

    content = Column(
        String(),
        nullable=False
    )

    creator = Column(
        String(),
        nullable=False
    )

    revealed = Column(
        Boolean(),
        nullable=False
    )

    story_id = Column(
        Uuid(),
        ForeignKey("stories.id", name="fk_events_story_id"),
        nullable=False
    )
