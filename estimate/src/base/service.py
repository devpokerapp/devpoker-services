from abc import abstractmethod
from nameko.rpc import rpc, RpcProxy
from nameko.events import EventDispatcher, event_handler
from nameko_sqlalchemy import DatabaseSession
from sqlalchemy.orm import Session
from base.models import DeclarativeBase


class BaseService:
    # NOTE: services must have the 'name' property

    db: Session = DatabaseSession(DeclarativeBase)
    gateway_rpc = RpcProxy('gateway_service')
    dispatch = EventDispatcher()

    @rpc
    def retrieve(self, sid, entity_id):
        # TODO
        pass

    @rpc
    def create(self, sid, payload):
        # TODO
        pass

    @rpc
    def update(self, sid, entity_id, payload):
        # TODO
        pass

    @rpc
    def delete(self, sid, entity_id):
        # TODO
        pass
