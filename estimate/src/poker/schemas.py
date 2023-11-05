from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from base.schemas import APIModel


class PokerCreate(APIModel):
    creator: str


class PokerUpdate(PokerCreate):
    current_story_id: UUID | None


class PokerRead(APIModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    creator: str
    current_story_id: UUID | None
