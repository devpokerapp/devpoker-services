from nameko.rpc import rpc, RpcProxy
from nameko.events import EventDispatcher, event_handler


class PokerService:
    name = "poker_service"

    gateway_rpc = RpcProxy('gateway_service')
    dispatch = EventDispatcher()

    @rpc
    def get(self, sid, entity_id):
        pass

    @rpc
    def create(self, sid, payload):
        pass

    @rpc
    def update(self, sid, entity_id, payload):
        pass

    @rpc
    def delete(self, sid, entity_id):
        pass

    @rpc
    def join(self, sid, channel: str):
        self.gateway_rpc.subscribe(sid, channel)
        self.gateway_rpc.broadcast(channel, 'join', sid)
