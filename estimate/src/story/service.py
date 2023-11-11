from nameko.rpc import rpc

from base.schemas import APIModel
from base.service import BaseService
from story.schemas import StoryRead, StoryCreate, StoryUpdate
from story.models import Story


class StoryService(BaseService):
    name = "story_service"

    entity_name = 'story'
    model = Story
    dto_read = StoryRead
    dto_create = StoryCreate
    dto_update = StoryUpdate

    @rpc
    def vote(self, sid, channel: str, vote: str):
        # TODO: move to EventService?
        self.gateway_rpc.broadcast(channel, 'vote', vote)
