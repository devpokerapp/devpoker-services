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
    story_id: str


class EventCreate(APIModel):
    type: Literal["vote", "comment", "action"]
    content: str
    story_id: str


class EventUpdate(APIModel):
    content: str
