from nameko.rpc import rpc
from base.service import BaseService


class StoryService(BaseService):
    name = "story_service"

    @rpc
    def vote(self, sid, channel: str, vote: str):
        # TODO: move to EventService?
        self.gateway_rpc.broadcast(channel, 'vote', vote)
