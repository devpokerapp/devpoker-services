import json

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from base.models import Model


class APIModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    @classmethod
    def to_json(cls, entity: Model) -> dict:
        result = cls.model_validate(entity)
        result = result.model_dump_json(by_alias=True)
        result = json.loads(result)  # converts to json and back to stringify Date and UUID
        return result


class SimpleModel(BaseModel):
    def to_json(self) -> dict:
        result = self.model_dump_json(by_alias=True)
        result = json.loads(result)
        return result


class Filter(SimpleModel):
    attr: str
    value: str


class QueryMetadata(SimpleModel):
    filters: list


class QueryRead(SimpleModel):
    items: list
    metadata: QueryMetadata


class SimpleListing(SimpleModel):
    items: list
