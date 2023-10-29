from nameko.rpc import rpc, RpcProxy


class StoryService:
    name = "story_service"

    gateway_rpc = RpcProxy('gateway_service')

    @rpc
    def create(self, sid, channel: str, vote: str):
        self.gateway_rpc.broadcast(channel, 'vote', vote)
