from datetime import datetime
from typing import Literal
from uuid import UUID

from base.schemas import APIModel


class EventRead(APIModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    type: Literal["vote", "comment", "action"]
    content: str
    creator: str
    revealed: bool
    story_id: UUID


class EventCreate(APIModel):
    type: Literal["vote", "comment", "action"]
    content: str
    story_id: UUID


class EventUpdate(APIModel):
    content: str
