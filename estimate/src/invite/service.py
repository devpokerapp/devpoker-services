import logging
import typing
import datetime
from uuid import UUID

from nameko.rpc import rpc

from base.converters import from_uuid, from_str
from base.exceptions import NotFound
from base.service import EntityService
from invite.models import Invite
from invite.schemas import InviteRead, InviteCreate, InviteUpdate
from utils import random_str

INVITE_CODE_SIZE = 48

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class InviteService(EntityService):
    name = "invite_service"

    entity_name = 'invite'
    model = Invite
    dto_read = InviteRead
    dto_create = InviteCreate
    dto_update = InviteUpdate
    broadcast_changes = False

    def get_query_column_converters(self) -> typing.Dict[str, typing.Callable[[any], str]]:
        return {
            'poker_id': from_uuid,
        }

    def get_room_name(self, entity):
        invite: Invite = entity
        return str(invite.poker_id)
    
    @rpc
    def create(self, sid, payload: dict) -> dict:
        code = random_str(INVITE_CODE_SIZE)

        dto = self.dto_create(**payload)
        entity = self.model(code=code, **dto.model_dump())

        self.db.add(entity)
        self.db.commit()

        logger.debug(f'created "{self.entity_name}" entity! {entity.id}; {entity.to_dict()}')

        result = self.dto_read.to_json(entity)

        self.handle_propagate(sid, self.event_created, entity, result)

        return result
    
    @rpc
    def validate(self, code: str, poker_id: UUID):
        now = datetime.datetime.now()
        entity = self.db.query(Invite) \
            .filter(Invite.code == code) \
            .filter(Invite.poker_id == poker_id) \
            .filter(Invite.expires_at > now) \
            .first()
        return entity is not None
