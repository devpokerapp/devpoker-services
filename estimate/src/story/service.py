import typing
from uuid import UUID

from nameko.rpc import rpc, RpcProxy
from nameko.events import event_handler

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

    def get_base_query(self):
        current_poker_id: UUID = self.gateway_rpc.get_current_poker_id()
        return self.db.query(Story).filter(Story.poker_id == current_poker_id)

    @event_handler("polling_service", "polling_completed")
    def handle_polling_completed(self, payload: dict):
        story_id = payload["storyId"]
        value = payload["value"]

        story = self.retrieve(sid=None, entity_id=story_id)

        self.update(sid=None, entity_id=story_id, payload={
            "name": story["name"],
            "description": story["description"],
            "pokerId": story["pokerId"],
            "value": value
        })

    @rpc
    def reveal(self, sid, entity_id: str):
        # TODO: remove this method
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

        entity_id = UUID(entity_id)

        entity = self.db.query(self.model) \
            .filter(self.model.id == entity_id) \
            .first()

        if entity is None:
            raise NotFound()

        result = self.dto_read.to_json(entity)
        self.handle_propagate(sid, 'story_revealed', entity, result)

        return result
