import logging
import typing
from uuid import UUID

from nameko.rpc import rpc

from base.converters import from_uuid, from_str
from base.exceptions import NotFound
from base.service import EntityService
from invite.models import Invite
from invite.schemas import InviteRead, InviteCreate, InviteUpdate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class InviteService(EntityService):
    name = "invite_service"

    entity_name = 'invite'
    model = Invite
    dto_read = InviteRead
    dto_create = InviteCreate
    dto_update = InviteUpdate
    broadcast_changes = True

    def get_query_column_converters(self) -> typing.Dict[str, typing.Callable[[any], str]]:
        return {
            'poker_id': from_uuid,
        }

    def get_room_name(self, entity):
        invite: Invite = entity
        return str(invite.poker_id)
