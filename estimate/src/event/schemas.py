from datetime import datetime
from typing import Literal
from uuid import UUID

from base.schemas import APIModel


EventType = Literal["vote", "comment", "action", "complete", "restart"]


class EventRead(APIModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    type: EventType
    content: str
    creator: str
    revealed: bool
    story_id: UUID
    poker_id: UUID


class EventCreate(APIModel):
    type: EventType
    content: str
    revealed: bool
    story_id: UUID


class EventUpdate(APIModel):
    content: str
    revealed: bool
