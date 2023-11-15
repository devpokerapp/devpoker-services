import logging

from nameko.rpc import rpc, RpcProxy

from base.service import BaseService, QueryRead
from poker.models import Poker
from poker.schemas import PokerRead, PokerCreate, PokerUpdate, PokerContext

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PokerService(BaseService):
    name = "poker_service"

    entity_name = "poker"
    model = Poker
    dto_read = PokerRead
    dto_create = PokerCreate
    dto_update = PokerUpdate

    story_rpc = RpcProxy("story_service")
    participant_rpc = RpcProxy("participant_service")

    @rpc
    def join(self, sid: str, participant_id: str, poker_id: str):
        participant = self.participant_rpc.retrieve(sid=None, entity_id=participant_id)

        self.gateway_rpc.subscribe(sid, poker_id)

        self.dispatch('poker_joined', participant)
        self.gateway_rpc.broadcast(poker_id, 'poker_joined', participant)

        return participant

    @rpc
    def context(self, sid: str, entity_id: str):
        filters = [{
            'attr': 'poker_id',
            'value': entity_id,
        }]

        poker = self.retrieve(sid=None, entity_id=entity_id)
        stories = self.story_rpc.query(sid=None, filters=filters)
        participants = self.participant_rpc.query(sid=None, filters=filters)

        stories = stories['items']
        participants = participants['items']

        result = PokerContext(poker=poker, stories=stories, participants=participants)
        result = result.to_json()

        self.gateway_rpc.unicast(sid, 'poker_context', result)

        return result

    @rpc
    def select_story(self, sid: str, poker_id: str, story_id: str):
        story = self.story_rpc.retrieve(sid=None, entity_id=story_id)
        poker = self.retrieve(sid=None, entity_id=poker_id)

        updated = self.update(sid=None, entity_id=poker_id, payload={
            "creator": poker['creator'],
            "current_story_id": story_id
        })

        self.gateway_rpc.broadcast(poker_id, 'poker_selected_story', story)
        self.dispatch('poker_selected_story', story)

        return story
