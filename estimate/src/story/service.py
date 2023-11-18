import typing

from nameko.rpc import rpc

from base.schemas import APIModel
from base.service import EntityService
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

    def get_query_column_converters(self) -> typing.Dict[str, typing.Callable[[any], str]]:
        return {
            'poker_id': from_uuid
        }

    def get_room_name(self, entity):
        story: Story = entity
        return str(story.poker_id)


    # TODO: story.context
