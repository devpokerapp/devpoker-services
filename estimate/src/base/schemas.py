import json
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from base.models import Model


class APIModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    @classmethod
    def to_json(cls, entity: Model):
        result = cls(**entity.to_dict())
        result = result.model_dump_json(by_alias=True)
        result = json.loads(result)  # converts to json and back to stringify Date and UUID
        return result
