from nameko.rpc import rpc

from base.schemas import APIModel
from base.service import BaseService
from participant.schemas import ParticipantRead, ParticipantCreate, ParticipantUpdate
from participant.models import Participant


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
