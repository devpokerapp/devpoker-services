import logging
from nameko.rpc import rpc, RpcProxy
from nameko.exceptions import RemoteError
from nameko.web.websocket import rpc as ws, WebSocketHub, WebSocketHubProvider

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GatewayService:
    name = "gateway_service"

    hub: WebSocketHub = WebSocketHubProvider()

    poker_rpc = RpcProxy("poker_service")
    story_rpc = RpcProxy("story_service")
    participant_rpc = RpcProxy("participant_service")
    event_rpc = RpcProxy("event_service")
    vote_rpc = RpcProxy("vote_service")

    @ws
    def request(self, sid, service, method, data, transaction_id=None):
        services = {
            'poker_service': self.poker_rpc,
            'story_service': self.story_rpc,
            'participant_service': self.participant_rpc,
            'event_service': self.event_rpc,
            'vote_service': self.vote_rpc,
        }

        logger.debug(f'called {service}:{method} by {sid}')

        result = None
        error = None
        success = False

        service_rpc = services.get(service)
        method_inst = getattr(service_rpc, method)

        try:
            result = method_inst(sid=sid, **data)
            success = True
        except RemoteError as exc:
            logger.error(f'error caused when calling {service}:{method} by {sid}. exception: {exc.value}')
            error = {
                'exc_type': exc.exc_type,
                'value': exc.value,
                'args': exc.args,
            }

        return {
            'success': success,
            'service': service,
            'method': method,
            'result': result,
            'error': error,
            'transaction_id': transaction_id,
        }

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
