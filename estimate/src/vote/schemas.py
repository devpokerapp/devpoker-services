from datetime import datetime
from uuid import UUID

from base.schemas import APIModel
from participant.schemas import ParticipantRead


class VotePlace(APIModel):
    content: str
    story_id: UUID


class VoteRead(APIModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    value: str
    participant_id: UUID
    polling_id: UUID
    participant: ParticipantRead = None


class VoteCreate(APIModel):
    value: str
    polling_id: UUID
    # participant_id comes from sid


class VoteUpdate(APIModel):
    value: str
