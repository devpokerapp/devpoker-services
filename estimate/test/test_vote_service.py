import uuid

import pytest
from nameko.testing.services import worker_factory
from pydantic import ValidationError

from base.exceptions import NotFound, InvalidFilter
from poker.models import Poker
from story.models import Story
from polling.models import Polling
from vote.models import Vote
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
        return {
            "items": []
        }

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
        return {
            "items": [
                {
                    "id": str(fake_event_id),
                    "type": "vote",
                    "content": "2",
                    "revealed": True,
                    "creator": str(fake_participant_id),
                    "storyId": str(fake_story_id1)
                }
            ]
        }

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


def test_when_retrieving_vote_should_return_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_participant_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()
    fake_polling_id = uuid.uuid4()
    fake_vote_id = uuid.uuid4()

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id, name="Story 1", poker_id=fake_poker_id))
    db_session.add(Participant(id=fake_participant_id, poker_id=fake_poker_id, name="Arthur", sid=fake_sid))
    db_session.commit()
    db_session.add(Polling(id=fake_polling_id, story_id=fake_story_id))
    db_session.commit()
    db_session.add(Vote(id=fake_vote_id, value="?", polling_id=fake_polling_id, participant_id=fake_participant_id))
    db_session.commit()

    service = worker_factory(VoteService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.retrieve(fake_sid, str(fake_vote_id))

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    assert 'pollingId' in result
    assert result['pollingId'] == str(fake_polling_id)
    assert 'participantId' in result
    assert result['participantId'] == str(fake_participant_id)
    assert 'value' in result
    assert result['value'] == "?"
    assert 'participant' in result
    assert type(result['participant']) is dict
    service.gateway_rpc.unicast.assert_called_once()
    service.dispatch.assert_called_once()
