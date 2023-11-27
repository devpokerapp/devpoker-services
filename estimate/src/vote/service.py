import typing
import logging
from uuid import UUID

from nameko.rpc import rpc, RpcProxy

from base.converters import from_uuid
from base.service import EntityService
from base.exceptions import NotFound, InvalidInput
from vote.schemas import VotePlace, VoteRead, VoteCreate, VoteUpdate
from vote.models import Vote
from polling.models import Polling

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class VoteService(EntityService):
    name = "vote_service"

    entity_name = "vote"
    model = Vote
    dto_read = VoteRead
    dto_create = VoteCreate
    dto_update = VoteUpdate
    broadcast_changes = True

    event_rpc = RpcProxy("event_service")
    polling_rpc = RpcProxy("polling_service")
    participant_rpc = RpcProxy("participant_service")

    def get_query_column_converters(self) -> typing.Dict[str, typing.Callable[[any], str]]:
        return {
            'participant_id': from_uuid,
            'polling_id': from_uuid
        }

    def get_room_name(self, entity) -> str:
        vote: Vote = entity
        polling: Polling = vote.polling
        return f'story:{polling.story_id}'

    @rpc
    def place(self, sid, payload: dict):
        dto = VotePlace(**payload)

        participant = self.participant_rpc.current(sid=sid)
        participant_id = UUID(participant['id'])

        polling = self.polling_rpc.retrieve(sid=None, entity_id=str(dto.polling_id))

        if polling["completed"]:
            raise InvalidInput()

        entity = self.db.query(self.model) \
            .filter(self.model.polling_id == dto.polling_id) \
            .filter(self.model.participant_id == participant_id) \
            .first()

        result: dict

        if entity is None:
            result = self.create(sid, {
                "value": dto.value,
                "pollingId": str(dto.polling_id)
            })
        else:  # vote already exists
            result = self.update(sid, str(entity.id), {
                "value": dto.value
            })

        room_name = f"story:{polling['storyId']}"
        self.gateway_rpc.broadcast(room_name, "vote_placed", result)
        self.dispatch("vote_placed", result)

        return result

    @rpc
    def create(self, sid, payload: dict) -> dict:
        participant = self.participant_rpc.current(sid=sid)
        participant_id = UUID(participant['id'])

        dto = self.dto_create(**payload)
        entity = self.model(participant_id=participant_id, **dto.model_dump())

        self.db.add(entity)
        self.db.commit()

        logger.debug(f'created "{self.entity_name}" entity! {entity.id}; {entity.to_dict()}')

        result = self.dto_read.to_json(entity)

        self.handle_propagate(sid, self.event_created, entity, result)

        return result
