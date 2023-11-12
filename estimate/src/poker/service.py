import logging

from nameko.rpc import rpc, RpcProxy

from base.service import BaseService
from poker.models import Poker
from poker.schemas import PokerRead, PokerCreate, PokerUpdate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PokerService(BaseService):
    name = "poker_service"

    entity_name = "poker"
    model = Poker
    dto_read = PokerRead
    dto_create = PokerCreate
    dto_update = PokerUpdate

    participant_rpc = RpcProxy("participant_service")
