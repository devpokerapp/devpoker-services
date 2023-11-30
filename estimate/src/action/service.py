from nameko.rpc import rpc, RpcProxy
from nameko.events import event_handler

from base.service import BaseService


class ActionService(BaseService):
    name = "action_service"

    event_rpc = RpcProxy("event_service")
    participant_rpc = RpcProxy("participant_service")

    def get_room_name(self, event: dict):
        return f'story:{event["storyId"]}'

    @event_handler("story_service", "story_revealed")
    def handle_story_revealed(self, payload: dict):
        self.event_rpc.create(sid=None, _system_event=True, payload={
            "type": "action",
            "content": "reveal",
            "creator": None,
            "revealed": True,
            "story_id": payload["id"]
        })
