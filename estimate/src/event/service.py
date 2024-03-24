import typing
import logging

from nameko.rpc import rpc, RpcProxy

from base.exceptions import NotFound
from base.converters import from_uuid, from_str, from_bool
from base.service import EntityService
from event.models import Event
from event.schemas import EventRead, EventCreate, EventUpdate
from story.models import Story
from participant.models import Participant

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class EventService(EntityService):
    name = "event_service"

    entity_name = 'event'
    model = Event
    dto_read = EventRead
    dto_create = EventCreate
    dto_update = EventUpdate
    broadcast_changes = True

    participant_rpc = RpcProxy("participant_service")

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

    def _get_current_creator(self, sid) -> str:
        participants = self.participant_rpc.query(sid=None, filters=[{
            "attr": "sid",
            "value": sid
        }])

        if len(participants) < 1:
            raise NotFound()

        participant = participants['items'][0]
        return str(participant['id'])

    @rpc
    def create(self, sid, payload: dict, _system_event: bool = False) -> dict:
        creator = 'system'
        if not _system_event:
            creator = self._get_current_creator(sid)

        dto = EventCreate(**payload)

        story = self.db.query(Story).filter(Story.id == dto.story_id).first()
        if story is None:
            raise NotFound()

        entity = self.model(creator=creator, poker_id=story.poker_id, **dto.model_dump())

        self.db.add(entity)
        self.db.commit()

        logger.debug(f'created "{self.entity_name}" entity! {entity.id}; {entity.to_dict()}')

        result = self.dto_read.to_json(entity)

        self.handle_propagate(sid, self.event_created, entity, result)

        return result
