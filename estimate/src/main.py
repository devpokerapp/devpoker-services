import logging
from nameko.rpc import rpc, RpcProxy
from nameko.web.websocket import rpc as ws, WebSocketHub, WebSocketHubProvider

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PokerService:
    name = "poker_service"

    gateway_rpc = RpcProxy('gateway_service')

    @rpc
    def create(self, sid, channel: str, vote: str):
        # logger.info(f"RECEIVED POKER! from {sid}: channel={channel}; vote={vote}")
        self.gateway_rpc.broadcast(channel, 'vote', vote)

    @rpc
    def join(self, sid, channel: str):
        # logger.info(f"SUBSCRIBING '{sid}' to '{channel}'")
        self.gateway_rpc.subscribe(sid, channel)
        self.gateway_rpc.broadcast(channel, 'join', sid)


class StoryService:
    name = "story_service"

    gateway_rpc = RpcProxy('gateway_service')

    @rpc
    def create(self, sid, channel: str, vote: str):
        # logger.info(f"RECEIVED USER STORY! from {sid}: channel={channel}; vote={vote}")
        self.gateway_rpc.broadcast(channel, 'vote', vote)
