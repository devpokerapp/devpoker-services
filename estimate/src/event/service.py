import typing

from base.converters import from_uuid, from_str, from_bool
from base.service import BaseService
from event.models import Event
from event.schemas import EventRead, EventCreate, EventUpdate


class EventService(BaseService):
    name = "event_service"

    entity_name = 'event'
    model = Event
    dto_read = EventRead
    dto_create = EventCreate
    dto_update = EventUpdate
    broadcast_changes = True

    def get_query_column_converters(self) -> typing.Dict[str, typing.Callable[[any], str]]:
        return {
            'type': from_str,
            'creator': from_str,
            'revealed': from_bool,
            'story_id': from_uuid
        }

    def get_room_name(self, entity) -> str:
        event: Event = entity
        return f'story:{event.story_id}'
