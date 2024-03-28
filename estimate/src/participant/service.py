import datetime
import logging
import typing
from uuid import UUID

from nameko.rpc import rpc, RpcProxy

from base.converters import from_uuid, from_str
from base.exceptions import NotFound, NotAllowed
from base.service import EntityService
from participant.models import Participant
from participant.schemas import (ParticipantRead, ParticipantCreate, ParticipantUpdate, ParticipantCreateWithInvite,
                                 ParticipantCreated, ParticipantJoin)
from participant.exceptions import InvalidInviteCode

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

    invite_rpc = RpcProxy('invite_service')

    def get_query_column_converters(self) -> typing.Dict[str, typing.Callable[[any], str]]:
        return {
            'sid': from_str,
            'poker_id': from_uuid,
            'keycloak_user_id': from_str
        }

    def get_room_name(self, entity):
        participant: Participant = entity
        return str(participant.poker_id)

    def get_base_query(self, sid):
        if sid is None:
            return super().get_base_query(sid)
        current_poker_id: UUID = self.gateway_rpc.get_current_poker_id(sid)
        return self.db.query(Participant).filter(Participant.poker_id == current_poker_id)

    @rpc
    def create(self, sid, payload: dict) -> dict:
        dto = ParticipantCreateWithInvite(**payload)
        
        valid = self.invite_rpc.validate(code=dto.invite_code, poker_id=dto.poker_id)
        if not valid:
            raise InvalidInviteCode()
        
        model_dto = ParticipantCreate(name=dto.name, poker_id=dto.poker_id,
                                      keycloak_user_id=dto.keycloak_user_id)
        entity = self.model(sid=sid, **model_dto.model_dump())

        self.db.add(entity)
        self.db.commit()

        logger.debug(f'created "{self.entity_name}" entity! {entity.id}; {entity.to_dict()}')

        result = ParticipantCreated.to_json(entity)

        self.handle_propagate(sid, self.event_created, entity, result)

        return result

    @rpc
    def update(self, sid, entity_id: str, payload: dict) -> dict:
        entity_id = UUID(entity_id)
        dto = ParticipantUpdate(**payload)

        entity = self.db.query(Participant) \
            .filter(Participant.id == entity_id) \
            .first()

        if entity is None:
            raise NotFound()

        if entity.secret_key != dto.secret_key:
            raise NotAllowed()

        # this method overrides default update to only update sid
        entity.sid = sid

        self.db.commit()

        logger.debug(f'update "{self.entity_name}" entity! {entity.id}; {entity.to_dict()}')

        result = self.dto_read.to_json(entity)

        self.handle_propagate(sid, self.event_updated, entity, result)

        return result

    @rpc
    def join(self, sid, entity_id: str, payload: dict) -> dict:
        entity_id = UUID(entity_id)
        dto = ParticipantJoin(**payload)

        entity = self.db.query(Participant) \
            .filter(Participant.id == entity_id) \
            .first()

        if entity is None:
            raise NotFound()

        if entity.secret_key != dto.secret_key:
            raise NotAllowed()

        # this method overrides default update to only update sid
        entity.sid = sid
        entity.updated_at = datetime.datetime.utcnow()  # forces updated_at change

        poker_id = str(entity.poker_id)

        self.db.commit()

        logger.debug(f'join participant! {entity.id}; {entity.to_dict()}')

        result = self.dto_read.to_json(entity)

        self.handle_propagate(sid, self.event_updated, entity, result)

        self.gateway_rpc.subscribe(sid, poker_id)
        self.dispatch('poker_joined', result)
        self.gateway_rpc.broadcast(poker_id, 'poker_joined', result)

        return result

    @rpc
    def current(self, sid) -> dict:
        """
        Finds the current participant used by a certain SID. This is useful to discover which poker session is being
        interacted.
        """

        """
        It's impossible to have more than one poker session being interacted in the same connection. But it's possible
        that the SID value repeats to many participants (e.g. if the user joins multiple sessions without resetting
        it's connection). So must consider updated_at in order to find the lastest logged participant with this SID.
        """
        # WARN: CANNOT use get_base_query. that function uses this function, causing infinite recursion
        entity = self.db.query(Participant) \
            .filter(Participant.sid == sid) \
            .order_by(Participant.updated_at.desc()) \
            .first()

        if entity is None:
            raise NotFound()

        result = self.dto_read.to_json(entity)

        return result
