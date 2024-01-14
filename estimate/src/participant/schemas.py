from datetime import datetime
from typing import Optional
from uuid import UUID

from base.schemas import APIModel


class ParticipantRead(APIModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    name: str
    sid: str
    poker_id: UUID
    keycloak_user_id: Optional[str] = None


class ParticipantCreate(APIModel):
    name: str
    # sid: str # provided by gateway
    poker_id: UUID
    keycloak_user_id: Optional[str] = None


class ParticipantUpdate(ParticipantCreate):
    pass
