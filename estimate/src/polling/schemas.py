from datetime import datetime
from typing import Optional, List
from uuid import UUID

from base.schemas import APIModel


class PollingRead(APIModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    value: Optional[str] = None
    completed: bool
    revealed: bool
    story_id: UUID
    # TODO: votes


class PollingCreate(APIModel):
    story_id: UUID


class PollingUpdate(APIModel):
    value: Optional[str] = None
    completed: bool
    revealed: bool
    story_id: UUID
