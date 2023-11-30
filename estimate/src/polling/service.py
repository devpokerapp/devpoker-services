import typing

from nameko.rpc import rpc
from nameko.events import event_handler

from base.converters import from_uuid, from_bool
from base.service import EntityService
from polling.models import Polling
from polling.schemas import PollingRead, PollingCreate, PollingUpdate


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
    def restart(self, sid, story_id):
        # TODO: complete old polling and creates a new one
        pass

    @rpc
    def complete(self, sid, story_id):
        # TODO: close the current polling. must define a value
        pass
