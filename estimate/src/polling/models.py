from sqlalchemy import Column, String, Boolean, Uuid, ForeignKey
from sqlalchemy.orm import relationship

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
        ForeignKey("stories.id", name="fk_pollings_story_id"),
        nullable=False
    )

    # TODO: relationships
    # TODO: schemas
