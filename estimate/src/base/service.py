import logging
from abc import abstractmethod
from uuid import UUID

from nameko.events import EventDispatcher
from nameko.rpc import rpc, RpcProxy
from nameko_sqlalchemy import DatabaseSession
from sqlalchemy.orm import Session

from base.exceptions import NotFound
from base.models import DeclarativeBase, Model
from base.schemas import APIModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BaseService:
    # NOTE: services must have the 'name' property

    db: Session = DatabaseSession(DeclarativeBase)
    gateway_rpc = RpcProxy('gateway_service')
    dispatch = EventDispatcher()

    @property
    @abstractmethod
    def entity_name(self) -> str:
        pass

    @property
    @abstractmethod
    def model(self) -> Model:
        pass

    @property
    @abstractmethod
    def dto_read(self) -> APIModel:
        pass

    @property
    @abstractmethod
    def dto_create(self) -> APIModel:
        pass

    @property
    @abstractmethod
    def dto_update(self) -> APIModel:
        pass

    @property
    def event_retrieved(self):
        return f"{self.entity_name}_retrieved"

    @property
    def event_created(self):
        return f"{self.entity_name}_created"

    @property
    def event_updated(self):
        return f"{self.entity_name}_updated"

    @property
    def event_deleted(self):
        return f"{self.entity_name}_deleted"

    @rpc
    def retrieve(self, sid, entity_id: str) -> dict:
        entity_id = UUID(entity_id)

        entity = self.db.query(self.model) \
            .filter(self.model.id == entity_id) \
            .first()

        if entity is None:
            raise NotFound()

        result = self.dto_read.to_json(entity)

        self.gateway_rpc.unicast(sid, self.event_retrieved, result)
        self.dispatch(self.event_retrieved, result)

        return result

    @rpc
    def create(self, sid, payload: dict) -> dict:
        dto = self.dto_create(**payload)
        entity = self.model(**dto.model_dump())

        self.db.add(entity)
        self.db.commit()

        logger.debug(f'created "{self.entity_name}" entity! {entity.id}; {entity.to_dict()}')

        result = self.dto_read.to_json(entity)

        self.gateway_rpc.unicast(sid, self.event_created, result)
        self.dispatch(self.event_created, result)

        return result

    @rpc
    def update(self, sid, entity_id: str, payload: dict) -> dict:
        entity_id = UUID(entity_id)

        entity = self.db.query(self.model)\
            .filter(self.model.id == entity_id)\
            .first()

        if entity is None:
            raise NotFound()

        dto = self.dto_update(**payload)
        values: dict = dto.model_dump()

        for key, value in values.items():
            setattr(entity, key, value)

        self.db.commit()

        logger.debug(f'update "{self.entity_name}" entity! {entity.id}; {entity.to_dict()}')

        result = self.dto_read.to_json(entity)

        self.gateway_rpc.unicast(sid, self.event_updated, result)
        self.dispatch(self.event_updated, result)

        return result

    @rpc
    def delete(self, sid, entity_id: str) -> dict:
        entity_id = UUID(entity_id)

        old = self.db.query(self.model) \
            .filter(self.model.id == entity_id) \
            .first()

        if old is None:
            raise NotFound()

        self.db.delete(old)
        self.db.commit()

        logger.debug(f'delete "{self.entity_name}" entity! {old.id}; {old.to_dict()}')

        result = self.dto_read.to_json(old)

        self.gateway_rpc.unicast(sid, self.event_deleted, result)
        self.dispatch(self.event_deleted, result)

        return result
