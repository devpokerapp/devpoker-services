from nameko.rpc import rpc, RpcProxy

from base.service import BaseService
from vote.schemas import VotePlace


class VoteService(BaseService):
    name = "vote_service"

    event_rpc = RpcProxy("event_service")
    participant_rpc = RpcProxy("participant_service")

    def get_room_name(self, event: dict):
        return f'story:{event["storyId"]}'

    @rpc
    def place(self, sid, payload: dict):
        dto = VotePlace(**payload)
        participant = self.participant_rpc.current(sid=sid)
        current_creator = participant['id']

        existing = self.event_rpc.query(sid=None, filters=[{
            "attr": "creator",
            "value": current_creator
        }, {
            "attr": "story_id",
            "value": str(dto.story_id)
        }, {
            "attr": "revealed",
            "value": "false"
        }])

        already_placed = len(existing) > 0
        result: dict

        if already_placed:  # update
            old = existing[0]
            result = self.event_rpc.update(sid=sid, entity_id=old['id'], payload={
                "content": dto.content,
                "revealed": False,
            })
        else:
            result = self.event_rpc.create(sid=sid, payload={
                "type": "vote",
                "content": dto.content,
                "revealed": False,
                "story_id": dto.story_id
            })

        # will also send the "event_updated" event
        self.gateway_rpc.broadcast(self.get_room_name(result), "vote_placed", result)
        self.dispatch("vote_placed", result)

        return result
