from datetime import datetime
from typing import Optional
from uuid import UUID

from base.schemas import APIModel


class StoryRead(APIModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    name: str
    poker_id: UUID
    description: Optional[str] = None
    value: Optional[str] = None


class StoryCreate(APIModel):
    name: str
    poker_id: UUID
    description: Optional[str] = None
    value: Optional[str] = None


class StoryUpdate(StoryCreate):
    # TODO
    pass
