import uuid

import pytest
from nameko.testing.services import worker_factory
from pydantic import ValidationError

from base.exceptions import NotFound, InvalidFilter
from poker.models import Poker
from story.models import Story
from event.models import Event
from participant.models import Participant
from vote.service import VoteService


def test_when_placing_vote_should_return_vote_event_as_dict():
    # arrange
    fake_sid = '1aaa'
    fake_poker_id1 = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_participant_id = uuid.uuid4()
    fake_event_id = uuid.uuid4()

    fake_payload = {
        "content": "5",
        "story_id": str(fake_story_id1)
    }

    def fake_event_query(*args, **kwargs):
        return []

    def fake_event_create(*args, **kwargs):
        return {
            "id": str(fake_event_id),
            "type": "vote",
            "content": "5",
            "revealed": False,
            "creator": str(fake_participant_id),
            "storyId": str(fake_story_id1)
        }

    def fake_event_update(*args, **kwargs):
        return {}

    def fake_participant_current(*args, **kwargs):
        return {
            "id": str(fake_participant_id),
            "name": "Arthur",
            "sid": fake_sid,
            "poker_id": str(fake_poker_id1),
        }

    service = worker_factory(VoteService)
    service.event_rpc.query.side_effect = fake_event_query
    service.event_rpc.create.side_effect = fake_event_create
    service.event_rpc.update.side_effect = fake_event_update
    service.participant_rpc.current.side_effect = fake_participant_current
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.place(fake_sid, fake_payload)

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert 'type' in result
    assert 'content' in result
    assert 'storyId' in result
    assert 'revealed' in result
    assert result['id'] is not None
    assert result['type'] == "vote"
    assert result['content'] == "5"
    assert result['revealed'] is False
    assert result['storyId'] == str(fake_story_id1)
    service.participant_rpc.current.assert_called_once()
    service.event_rpc.query.assert_called_once()
    service.event_rpc.create.assert_called_once()
    service.event_rpc.update.assert_not_called()
    service.gateway_rpc.broadcast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_placing_vote_before_its_revealed_should_replace_current_vote(monkeypatch):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id1 = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_participant_id = uuid.uuid4()
    fake_event_id = uuid.uuid4()

    fake_payload = {
        "content": "5",
        "story_id": str(fake_story_id1)
    }

    def fake_event_query(*args, **kwargs):
        return [
            {
                "id": str(fake_event_id),
                "type": "vote",
                "content": "2",
                "revealed": True,
                "creator": str(fake_participant_id),
                "storyId": str(fake_story_id1)
            }
        ]

    def fake_event_create(*args, **kwargs):
        return {}

    def fake_event_update(*args, **kwargs):
        return {
            "id": str(fake_event_id),
            "type": "vote",
            "content": "5",
            "revealed": False,
            "creator": str(fake_participant_id),
            "storyId": str(fake_story_id1)
        }

    def fake_participant_current(*args, **kwargs):
        return {
            "id": str(fake_participant_id),
            "name": "Arthur",
            "sid": fake_sid,
            "poker_id": str(fake_poker_id1),
        }

    service = worker_factory(VoteService)
    service.event_rpc.query.side_effect = fake_event_query
    service.event_rpc.create.side_effect = fake_event_create
    service.event_rpc.update.side_effect = fake_event_update
    service.participant_rpc.current.side_effect = fake_participant_current
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.place(fake_sid, fake_payload)

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert 'type' in result
    assert 'content' in result
    assert 'storyId' in result
    assert 'revealed' in result
    assert result['id'] is not None
    assert result['type'] == "vote"
    assert result['content'] == "5"
    assert result['revealed'] is False
    assert result['storyId'] == str(fake_story_id1)
    service.participant_rpc.current.assert_called_once()
    service.event_rpc.query.assert_called_once()
    service.event_rpc.create.assert_not_called()
    service.event_rpc.update.assert_called_once()
    service.gateway_rpc.broadcast.assert_called_once()
    service.dispatch.assert_called_once()
