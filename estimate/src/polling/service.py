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
    def restart(self, sid, story_id):
        # TODO: complete old polling and creates a new one
        pass

    @rpc
    def complete(self, sid, payload):
        dto = PollingComplete(**payload)

        entity: Optional[Polling] = self.db.query(Polling) \
            .filter(Polling.id == dto.id) \
            .first()

        if entity is None:
            raise NotFound()

        entity.value = dto.value
        entity.completed = True

        self.db.commit()

        logger.debug(f'completed "{self.entity_name}" entity! {entity.id}; {entity.to_dict()}')

        result = self.dto_read.to_json(entity)

        self.handle_propagate(sid, 'polling_completed', entity, result)
        self.handle_propagate(sid, self.event_updated, entity, result)

        return result
