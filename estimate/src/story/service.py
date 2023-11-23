import typing
from uuid import UUID

from nameko.rpc import rpc, RpcProxy

from base.schemas import APIModel
from base.service import EntityService
from base.exceptions import NotFound
from base.converters import from_uuid, from_str
from story.schemas import StoryRead, StoryCreate, StoryUpdate
from story.models import Story


class StoryService(EntityService):
    name = "story_service"

    entity_name = 'story'
    model = Story
    dto_read = StoryRead
    dto_create = StoryCreate
    dto_update = StoryUpdate
    broadcast_changes = True

    event_rpc = RpcProxy("event_service")

    def get_query_column_converters(self) -> typing.Dict[str, typing.Callable[[any], str]]:
        return {
            'poker_id': from_uuid
        }

    def get_room_name(self, entity):
        story: Story = entity
        return str(story.poker_id)

    @rpc
    def reveal(self, sid, entity_id: str):
        unrevealed_events = self.event_rpc.query(sid=None, filters=[{
            "attr": "story_id",
            "value": entity_id
        }, {
            "attr": "revealed",
            "value": "false"
        }])

        for event in unrevealed_events['items']:
            self.event_rpc.update(sid=sid, entity_id=event['id'], payload={
                "content": event["content"],
                "revealed": True
            })

        # TODO: register reveal action

        entity_id = UUID(entity_id)

        entity = self.db.query(self.model) \
            .filter(self.model.id == entity_id) \
            .first()

        if entity is None:
            raise NotFound()

        result = self.dto_read.to_json(entity)
        self.handle_propagate(sid, 'story_revealed', entity, result)

        return result
