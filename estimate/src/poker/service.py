import logging
import json
from nameko.rpc import rpc, RpcProxy
from nameko.events import EventDispatcher, event_handler
from nameko_sqlalchemy import DatabaseSession
from base.models import DeclarativeBase
from poker.models import Poker
from story.models import Story
from event.models import Event
from poker.schemas import PokerCreate, PokerRead


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PokerService:
    name = "poker_service"

    db = DatabaseSession(DeclarativeBase)
    gateway_rpc = RpcProxy('gateway_service')
    dispatch = EventDispatcher()

    @rpc
    def get(self, sid, entity_id):
        pass

    @rpc
    def create(self, sid, payload: dict):
        dto = PokerCreate(**payload)
        entity = Poker(creator=dto.creator)

        self.db.add(entity)
        self.db.commit()

        logger.debug(f'created poker entity! {entity.id}; {entity.to_dict()}')

        result = PokerRead(**entity.to_dict())
        result = result.model_dump_json()
        result = json.loads(result)

        self.gateway_rpc.unicast(sid, 'poker_created', result)
        self.dispatch('poker_created', result)

        return result

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
