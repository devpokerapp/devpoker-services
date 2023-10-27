import logging
from nameko.web.websocket import rpc, WebSocketHub, WebSocketHubProvider

logger = logging.getLogger(__name__)


class PokerService:
    name = "poker_service"
    hub: WebSocketHub = WebSocketHubProvider()

    @rpc
    def create(self, sid, channel: str, vote: str):
        logger.info(f"RECEIVED POKER! from {sid}: channel={channel}; vote={vote}")
        self.hub.broadcast(channel, 'vote', vote)

    @rpc
    def join(self, sid, channel: str):
        logger.info(f"SUBSCRIBING '{sid}' to '{channel}'")
        self.hub.subscribe(sid, channel)
        self.hub.broadcast(channel, 'join', sid)


class StoryService:
    name = "story_service"
    hub: WebSocketHub = WebSocketHubProvider()

    @rpc
    def create(self, sid, channel: str, vote: str):
        logger.info(f"RECEIVED USER STORY! from {sid}: channel={channel}; vote={vote}")
        self.hub.broadcast(channel, 'vote', vote)
