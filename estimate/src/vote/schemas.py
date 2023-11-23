from uuid import UUID
from base.schemas import APIModel


class VotePlace(APIModel):
    content: str
    story_id: UUID
