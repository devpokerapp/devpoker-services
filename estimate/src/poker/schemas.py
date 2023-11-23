from datetime import datetime
from uuid import UUID
from typing import List
from pydantic import BaseModel
from base.schemas import APIModel, SimpleModel
from story.schemas import StoryRead
from participant.schemas import ParticipantRead


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
    stories: List[StoryRead] = None
    participants: List[ParticipantRead] = None


class PokerContext(SimpleModel):
    poker: dict
    stories: list
    participants: list
