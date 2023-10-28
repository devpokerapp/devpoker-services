import logging
from nameko.rpc import rpc, RpcProxy
from nameko.web.websocket import rpc as ws, WebSocketHub, WebSocketHubProvider

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GatewayService:
    name = "gateway_service"

    hub: WebSocketHub = WebSocketHubProvider()

    poker_rpc = RpcProxy("poker_service")
    story_rpc = RpcProxy("story_service")

    @ws
    def request(self, sid, service, method, data):
        services = {
            'poker_service': self.poker_rpc,
            'story_service': self.story_rpc
        }

        logger.debug(f'called {service}:{method} by {sid}')

        service_rpc = services.get(service)
        method_inst = getattr(service_rpc, method)
        method_inst(sid, **data)

    @rpc
    def unicast(self, sid, event, data):
        logger.debug(f'unicasted event {event} to sid {sid}')
        self.hub.unicast(sid, event, data)

    @rpc
    def broadcast(self, channel, event, data):
        logger.debug(f'broadcasted event {event} to channel {channel}')
        self.hub.broadcast(channel, event, data)

    @rpc
    def subscribe(self, sid, channel):
        logger.debug(f'subscribed {sid} to channel {channel}')
        self.hub.subscribe(sid, channel)

    @rpc
    def unsubscribe(self, sid, channel):
        logger.debug(f'unsubscribed {sid} from channel {channel}')
        self.hub.unsubscribe(sid, channel)


class PokerService:
    name = "poker_service"

    gateway_rpc = RpcProxy('gateway_service')

    @rpc
    def create(self, sid, channel: str, vote: str):
        logger.info(f"RECEIVED POKER! from {sid}: channel={channel}; vote={vote}")
        self.gateway_rpc.broadcast(channel, 'vote', vote)

    @rpc
    def join(self, sid, channel: str):
        logger.info(f"SUBSCRIBING '{sid}' to '{channel}'")
        self.gateway_rpc.subscribe(sid, channel)
        self.gateway_rpc.broadcast(channel, 'join', sid)


class StoryService:
    name = "story_service"

    gateway_rpc = RpcProxy('gateway_service')

    @rpc
    def create(self, sid, channel: str, vote: str):
        logger.info(f"RECEIVED USER STORY! from {sid}: channel={channel}; vote={vote}")
        self.gateway_rpc.broadcast(channel, 'vote', vote)
