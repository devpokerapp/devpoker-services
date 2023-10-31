from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class PokerCreate(BaseModel):
    creator: str


class PokerRead(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    creator: str
    current_story_id: UUID | None
