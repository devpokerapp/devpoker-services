import logging

from nameko.rpc import rpc, RpcProxy
from nameko.events import event_handler

from base.service import BaseService


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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

    @event_handler("polling_service", "polling_completed")
    def handle_polling_completed(self, payload: dict):
        result = self.event_rpc.create(sid=None, _system_event=True, payload={
            "type": "complete",
            "content": payload["value"],
            "creator": None,
            "revealed": True,
            "story_id": payload["storyId"]
        })
        logger.debug(f'registered complete event for story {payload["storyId"]}! {result}')

    @event_handler("polling_service", "polling_restarted")
    def handle_polling_restarted(self, payload: dict):
        result = self.event_rpc.create(sid=None, _system_event=True, payload={
            "type": "restart",
            "content": payload["id"],
            "creator": None,
            "revealed": True,
            "story_id": payload["storyId"]
        })
        logger.debug(f'registered restart event for story {payload["storyId"]}! {result}')
