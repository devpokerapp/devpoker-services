from datetime import datetime
from typing import Optional, List
from uuid import UUID

from base.schemas import APIModel
from vote.schemas import VoteRead


class PollingRead(APIModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    value: Optional[str] = None
    completed: bool
    revealed: bool
    anonymous: bool
    story_id: UUID
    poker_id: UUID
    votes: List[VoteRead] = None


class PollingCreate(APIModel):
    story_id: UUID


class PollingUpdate(APIModel):
    value: Optional[str] = None
    completed: bool
    revealed: bool
    story_id: UUID


class PollingComplete(APIModel):
    id: str
    value: str
