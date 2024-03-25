import logging
import datetime
from uuid import UUID
from typing import Union

from nameko.rpc import rpc, RpcProxy

from base.service import EntityService, QueryRead
from base.exceptions import NotFound, NotAllowed
from poker.models import Poker
from poker.schemas import PokerRead, PokerCreate, PokerUpdate, PokerContext
from participant.models import Participant
from invite.models import Invite

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PokerService(EntityService):
    name = "poker_service"

    entity_name = "poker"
    model = Poker
    dto_read = PokerRead
    dto_create = PokerCreate
    dto_update = PokerUpdate
    broadcast_changes = True

    story_rpc = RpcProxy("story_service")
    participant_rpc = RpcProxy("participant_service")
    invite_rpc = RpcProxy("invite_service")

    def get_room_name(self, entity) -> str:
        poker: Poker = entity
        return str(poker.id)

    def get_base_query(self, sid):
        current_poker_id: UUID = self.gateway_rpc.get_current_poker_id(sid)
        return self.db.query(Poker).filter(Poker.id == current_poker_id)

    @rpc
    def start(self, sid, payload: dict) -> dict:
        poker = self.create(sid=sid, payload=payload)
        invite = self.invite_rpc.create(sid=sid, payload={
            'pokerId': poker['id'],
            'expiresAt': str(datetime.datetime.now() + datetime.timedelta(hours=1))
        })
        self.gateway_rpc.unicast(sid, 'poker_started', invite)

    # TODO: leave event

    @rpc
    def select_story(self, sid: str, poker_id: str, story_id: Union[str | None] = None):
        poker = self.retrieve(sid=None, entity_id=poker_id)

        story = None
        if story_id is not None:
            story = self.story_rpc.retrieve(sid=None, entity_id=story_id)

        updated = self.update(sid=None, entity_id=poker_id, payload={
            "creator": poker['creator'],
            "vote_pattern": poker['votePattern'],
            "current_story_id": story_id
        })

        self.gateway_rpc.broadcast(poker_id, 'poker_selected_story', story)
        self.dispatch('poker_selected_story', story)

        return story
