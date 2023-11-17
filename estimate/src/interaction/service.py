from nameko.rpc import rpc, RpcProxy
from nameko.events import event_handler, EventDispatcher

from base.schemas import APIModel
from participant.schemas import ParticipantRead, ParticipantCreate, ParticipantUpdate
from participant.models import Participant


class InteractionService:
    name = "interaction_service"

    gateway_rpc = RpcProxy('gateway_service')
    dispatch = EventDispatcher()

    # TODO: handle events and throw to poker room
    # story create, update, delete
    # poker join?
