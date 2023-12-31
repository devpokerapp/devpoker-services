import logging
import typing
from uuid import UUID

from nameko.rpc import rpc

from base.converters import from_uuid, from_str
from base.exceptions import NotFound
from base.service import EntityService
from participant.models import Participant
from participant.schemas import ParticipantRead, ParticipantCreate, ParticipantUpdate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ParticipantService(EntityService):
    name = "participant_service"

    entity_name = 'participant'
    model = Participant
    dto_read = ParticipantRead
    dto_create = ParticipantCreate
    dto_update = ParticipantUpdate
    broadcast_changes = True

    def get_query_column_converters(self) -> typing.Dict[str, typing.Callable[[any], str]]:
        return {
            'sid': from_str,
            'poker_id': from_uuid
        }

    def get_room_name(self, entity):
        participant: Participant = entity
        return str(participant.poker_id)

    @rpc
    def create(self, sid, payload: dict) -> dict:
        dto = self.dto_create(**payload)
        entity = self.model(sid=sid, **dto.model_dump())

        self.db.add(entity)
        self.db.commit()

        logger.debug(f'created "{self.entity_name}" entity! {entity.id}; {entity.to_dict()}')

        result = self.dto_read.to_json(entity)

        self.handle_propagate(sid, self.event_created, entity, result)

        return result

    @rpc
    def update(self, sid, entity_id: str, payload: dict) -> dict:
        entity_id = UUID(entity_id)

        entity = self.db.query(self.model) \
            .filter(self.model.id == entity_id) \
            .first()

        if entity is None:
            raise NotFound()

        # this method overrides default update to only update sid
        entity.sid = sid

        self.db.commit()

        logger.debug(f'update "{self.entity_name}" entity! {entity.id}; {entity.to_dict()}')

        result = self.dto_read.to_json(entity)

        self.handle_propagate(sid, self.event_updated, entity, result)

        return result

    @rpc
    def current(self, sid) -> dict:
        entity = self.db.query(self.model) \
            .filter(self.model.sid == sid) \
            .first()

        if entity is None:
            raise NotFound()

        result = self.dto_read.to_json(entity)

        return result
