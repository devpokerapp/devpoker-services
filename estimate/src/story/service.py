import typing

from nameko.rpc import rpc

from base.schemas import APIModel
from base.service import BaseService
from base.converters import from_uuid, from_str
from story.schemas import StoryRead, StoryCreate, StoryUpdate
from story.models import Story


class StoryService(BaseService):
    name = "story_service"

    entity_name = 'story'
    model = Story
    dto_read = StoryRead
    dto_create = StoryCreate
    dto_update = StoryUpdate
    broadcast_changes = True

    def get_query_column_converters(self) -> typing.Dict[str, typing.Callable[[any], str]]:
        return {
            'name': from_str,
            'poker_id': from_uuid
        }

    def get_room_name(self, entity):
        story: Story = entity
        return str(story.poker_id)

    @rpc
    def vote(self, sid, channel: str, vote: str):
        # TODO: move to EventService?
        self.gateway_rpc.broadcast(channel, 'vote', vote)
