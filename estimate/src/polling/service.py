import typing
import logging
from typing import Optional
from uuid import UUID

from nameko.rpc import rpc, RpcProxy
from nameko.events import event_handler

from base.exceptions import NotFound
from base.converters import from_uuid, from_bool
from base.service import EntityService
from polling.models import Polling
from polling.schemas import PollingRead, PollingCreate, PollingUpdate, PollingComplete

logger = logging.getLogger(__name__)


class PollingService(EntityService):
    name = "polling_service"

    entity_name = 'polling'
    model = Polling
    dto_read = PollingRead
    dto_create = PollingCreate
    dto_update = PollingUpdate
    broadcast_changes = True

    def get_query_column_converters(self) -> typing.Dict[str, typing.Callable[[any], str]]:
        return {
            'completed': from_bool,
            'revealed': from_bool,
            'story_id': from_uuid
        }

    def get_room_name(self, entity):
        polling: Polling = entity
        return f'story:{str(polling.story_id)}'

    @event_handler("story_service", "story_created")
    def handle_story_created(self, payload: dict):
        # crates a new polling for every new story
        self.create(sid=None, payload={
            "storyId": payload['id']
        })

    @rpc
    def current(self, sid, story_id):
        story_id = UUID(story_id)

        entity = self.db.query(Polling) \
            .filter(Polling.story_id == story_id) \
            .filter(Polling.completed == False) \
            .order_by(Polling.created_at.desc()) \
            .first()

        if entity is None:
            raise NotFound()

        result = self.dto_read.to_json(entity)

        return result

    @rpc
    def complete(self, sid, payload):
        dto = PollingComplete(**payload)

        original = self.retrieve(sid=None, entity_id=dto.id)

        result = self.update(sid=sid, entity_id=dto.id, payload={
            "value": dto.value,
            "completed": True,
            "revealed": True,
            "storyId": original["storyId"],
        })

        logger.debug(f'completed "{self.entity_name}" entity! {result["id"]};')

        room_name = f'story:{result["storyId"]}'
        self.dispatch('polling_completed', result)
        self.gateway_rpc.broadcast(room_name, 'polling_completed', result)

        return result

    @rpc
    def restart(self, sid, entity_id):
        original = self.retrieve(sid=None, entity_id=entity_id)
        story_id = original["storyId"]

        # completes current polling
        completed = self.update(sid=sid, entity_id=entity_id, payload={
            **original,
            "completed": True,
        })

        # starts a new polling
        result = self.create(sid=sid, payload={
            "storyId": story_id
        })

        room_name = f'story:{story_id}'
        self.dispatch('polling_restarted', result)
        self.gateway_rpc.broadcast(room_name, 'polling_restarted', result)
