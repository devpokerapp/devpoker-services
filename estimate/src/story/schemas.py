from datetime import datetime
from typing import Optional, List
from uuid import UUID

from base.schemas import APIModel
from event.schemas import EventRead


class StoryRead(APIModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    name: str
    poker_id: UUID
    description: Optional[str] = None
    value: Optional[str] = None
    events: List[EventRead] = None


class StoryCreate(APIModel):
    name: str
    poker_id: UUID
    description: Optional[str] = None
    value: Optional[str] = None


class StoryUpdate(StoryCreate):
    pass
