import typing

from nameko.rpc import rpc, RpcProxy

from base.converters import from_uuid
from base.service import EntityService
from vote.schemas import VotePlace, VoteRead, VoteCreate, VoteUpdate
from vote.models import Vote
from polling.models import Polling


class VoteService(EntityService):
    name = "vote_service"

    entity_name = "vote"
    model = Vote
    dto_read = VoteRead
    dto_create = VoteCreate
    dto_update = VoteUpdate
    broadcast_changes = True

    event_rpc = RpcProxy("event_service")
    participant_rpc = RpcProxy("participant_service")

    def get_query_column_converters(self) -> typing.Dict[str, typing.Callable[[any], str]]:
        return {
            'participant_id': from_uuid,
            'polling_id': from_uuid
        }

    def get_room_name(self, entity) -> str:
        vote: Vote = entity
        polling: Polling = vote.polling
        return f'story:{polling.story_id}'

    @rpc
    def place(self, sid, payload: dict):
        # TODO: use Vote entity instead of events
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

        already_placed = len(existing['items']) > 0
        result: dict

        if already_placed:  # update
            old = existing['items'][0]
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
