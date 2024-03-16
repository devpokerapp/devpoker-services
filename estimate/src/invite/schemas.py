from datetime import datetime
from typing import Optional
from uuid import UUID

from base.schemas import APIModel


class InviteRead(APIModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    code: str
    expires_at: datetime
    poker_id: UUID


class InviteCreate(APIModel):
    poker_id: UUID
    expires_at: datetime


class InviteUpdate(InviteCreate):
    pass
