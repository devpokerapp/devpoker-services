import logging

from nameko.rpc import rpc

from base.service import BaseService
from participant.models import Participant
from participant.schemas import ParticipantRead, ParticipantCreate, ParticipantUpdate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ParticipantService(BaseService):
    name = "participant_service"

    entity_name = 'participant'
    model = Participant
    dto_read = ParticipantRead
    dto_create = ParticipantCreate
    dto_update = ParticipantUpdate
    broadcast_changes = True

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
