import logging
import typing
from abc import abstractmethod
from uuid import UUID

from nameko.events import EventDispatcher
from nameko.rpc import rpc, RpcProxy
from nameko_sqlalchemy import DatabaseSession
from sqlalchemy.orm import Session

from base.exceptions import NotFound, InvalidFilter
from base.models import DeclarativeBase, Model
from base.schemas import APIModel, Filter, QueryMetadata, QueryRead

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BaseService:
    # NOTE: services must have the 'name' property

    db: Session = DatabaseSession(DeclarativeBase)
    gateway_rpc = RpcProxy('gateway_service')
    dispatch = EventDispatcher()

    broadcast_changes: bool = False

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

    @abstractmethod
    def get_query_column_converters(self) -> typing.Dict[str, typing.Callable[[any], str]]:
        """
        Defines how to convert strings received from query filters. The column
        is defined by the dict key. The value is a converter function. Columns
        not present on the dict will be considered as disabled for querying.

        A set of sample converters can be found in `base.converters`
        """
        return dict()

    @property
    def event_queried(self):
        return f"{self.entity_name}_queried"

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

    @abstractmethod
    def get_room_name(self, entity) -> str:
        pass

    def handle_propagate(self, sid, event: str, entity, payload: dict):
        self.dispatch(event, payload)

        if self.broadcast_changes:
            room_name = self.get_room_name(entity)
            self.gateway_rpc.broadcast(room_name, event, payload)
        else:
            self.gateway_rpc.unicast(sid, event, payload)

    @rpc
    def query(self, sid, filters: list[dict]) -> dict:
        """
        Queries the stored entities based on a list of filters

        Only does unicast
        """
        applied_filters = list()
        column_converters = self.get_query_column_converters()

        for f in filters:
            filter = Filter(**f)
            if filter.attr not in column_converters.keys():
                raise InvalidFilter(filter.attr)
            converter = column_converters.get(filter.attr)
            try:
                converted_value = converter(filter.value)
            except Exception as exc:
                logger.error(f'Unable to convert filter value. attr: {filter.attr}; value: {filter.value}')
                raise InvalidFilter(filter.attr)
            applied_filters.append(getattr(self.model, filter.attr) == converted_value)

        entities = self.db.query(self.model) \
            .filter(*applied_filters) \
            .all()

        items = []
        metadata = QueryMetadata(filters=filters)

        for entity in entities:
            items.append(self.dto_read.to_json(entity))

        result = QueryRead(items=items, metadata=metadata)
        result = result.to_json()

        self.dispatch(self.event_queried, result)
        self.gateway_rpc.unicast(sid, self.event_queried, result)

        return result

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

        self.handle_propagate(sid, self.event_created, entity, result)

        return result

    @rpc
    def update(self, sid, entity_id: str, payload: dict) -> dict:
        entity_id = UUID(entity_id)

        entity = self.db.query(self.model) \
            .filter(self.model.id == entity_id) \
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

        self.handle_propagate(sid, self.event_updated, entity, result)

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

        self.handle_propagate(sid, self.event_deleted, old, result)

        return result
