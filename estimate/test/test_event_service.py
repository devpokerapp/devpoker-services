import uuid

import pytest
from nameko.testing.services import worker_factory
from pydantic import ValidationError

from base.exceptions import NotFound, InvalidFilter
from poker.models import Poker
from story.models import Story
from event.models import Event
from participant.models import Participant
from event.service import EventService


def test_when_querying_revealed_events_from_story_should_return_only_revealed_from_that_story(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id1 = uuid.uuid4()
    fake_poker_id2 = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_story_id2 = uuid.uuid4()
    fake_story_id3 = uuid.uuid4()
    fake_event_id_revealed = uuid.uuid4()
    fake_event_id_not_revealed = uuid.uuid4()
    fake_event_id_not_revealed_from_another = uuid.uuid4()

    fake_filters = [
        {
            "attr": "revealed",
            "value": "false"
        },
        {
            "attr": "story_id",
            "value": str(fake_story_id1)
        }
    ]

    db_session.add(Poker(id=fake_poker_id1, creator='user@test.com'))
    db_session.add(Poker(id=fake_poker_id2, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id1, name="Story 1", poker_id=fake_poker_id1))
    db_session.add(Story(id=fake_story_id2, name="Story 2", poker_id=fake_poker_id1))
    db_session.add(Story(id=fake_story_id3, name="Story from other poker", poker_id=fake_poker_id2))
    db_session.commit()
    db_session.add(Event(id=fake_event_id_revealed, story_id=fake_story_id1, type="vote",
                         revealed=True, content="5", creator="user1"))
    db_session.add(Event(id=fake_event_id_not_revealed, story_id=fake_story_id1, type="vote",
                         revealed=False, content="2", creator="user1"))
    db_session.add(Event(id=fake_event_id_not_revealed_from_another, story_id=fake_story_id2, type="vote",
                         revealed=False, content="2", creator="user1"))
    db_session.commit()

    service = worker_factory(EventService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.query(fake_sid, fake_filters)

    # assert
    assert type(result) is dict
    assert 'items' in result
    assert 'metadata' in result
    assert type(result['items']) is list
    assert type(result['metadata']) is dict
    assert len(result['items']) == 1
    assert 'id' in result['items'][0]
    assert result['items'][0]['id'] == str(fake_event_id_not_revealed)
    assert 'filters' in result['metadata']
    assert type(result['metadata']['filters']) is list
    assert len(result['metadata']['filters']) == len(fake_filters)
    assert type(result['metadata']['filters'][0]) is dict
    assert 'attr' in result['metadata']['filters'][0]
    assert 'value' in result['metadata']['filters'][0]
    assert type(result['metadata']['filters'][0]['attr']) is str
    assert type(result['metadata']['filters'][0]['value']) is str
    assert result['metadata']['filters'][0]['attr'] == 'revealed'
    assert result['metadata']['filters'][0]['value'] == 'false'
    service.gateway_rpc.unicast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_creating_event_should_return_as_dict(db_session, monkeypatch):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id1 = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_participant_id = uuid.uuid4()

    fake_payload = {
        "type": "vote",
        "content": "5",
        "revealed": "false",
        "story_id": str(fake_story_id1)
    }

    db_session.add(Poker(id=fake_poker_id1, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id1, poker_id=fake_poker_id1, name="Story 1"))
    db_session.add(Participant(id=fake_participant_id, poker_id=fake_poker_id1, name="Arthur", sid=fake_sid))
    db_session.commit()

    def fake_get_creator(*args, **kwargs):
        return str(fake_participant_id)

    service = worker_factory(EventService, db=db_session)
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    monkeypatch.setattr(service, "_get_current_creator", fake_get_creator)

    # act
    result = service.create(fake_sid, fake_payload)

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
    service.gateway_rpc.broadcast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_creating_event_with_invalid_type_should_cause_error(db_session, monkeypatch):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id1 = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_participant_id = uuid.uuid4()

    fake_payload = {
        "type": "bizarre_event",
        "content": "a",
        "revealed": "false",
        "story_id": str(fake_story_id1)
    }

    db_session.add(Poker(id=fake_poker_id1, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id1, poker_id=fake_poker_id1, name="Story 1"))
    db_session.add(Participant(id=fake_participant_id, poker_id=fake_poker_id1, name="Arthur", sid=fake_sid))
    db_session.commit()

    def fake_get_creator(*args, **kwargs):
        return str(fake_participant_id)

    service = worker_factory(EventService, db=db_session)
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    monkeypatch.setattr(service, "_get_current_creator", fake_get_creator)

    # act
    # assert
    with pytest.raises(ValidationError):
        result = service.create(fake_sid, fake_payload)


def test_when_creating_event_with_valid_participant_should_return_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id1 = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_participant_id = uuid.uuid4()

    fake_payload = {
        "type": "vote",
        "content": "5",
        "revealed": "false",
        "story_id": str(fake_story_id1)
    }

    db_session.add(Poker(id=fake_poker_id1, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id1, poker_id=fake_poker_id1, name="Story 1"))
    db_session.add(Participant(id=fake_participant_id, poker_id=fake_poker_id1, name="Arthur", sid=fake_sid))
    db_session.commit()

    def fake_query_participants(*args, **kwargs):
        return {
            "items": [
                {
                    "id": str(fake_participant_id),
                    "pokerId": str(fake_poker_id1),
                    "name": "Arthur",
                    "sid": fake_sid
                }
            ]
        }

    service = worker_factory(EventService, db=db_session)
    service.participant_rpc.query.side_effect = fake_query_participants
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.create(fake_sid, fake_payload)

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert 'type' in result
    assert 'content' in result
    assert 'storyId' in result
    assert 'revealed' in result
    assert 'creator' in result
    assert result['id'] is not None
    assert result['type'] == "vote"
    assert result['content'] == "5"
    assert result['revealed'] is False
    assert result['storyId'] == str(fake_story_id1)
    assert result['creator'] == str(fake_participant_id)
    service.gateway_rpc.broadcast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_creating_event_with_non_existing_participant_should_cause_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id1 = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_participant_id = uuid.uuid4()

    fake_payload = {
        "type": "bizarre_event",
        "content": "a",
        "revealed": "false",
        "story_id": str(fake_story_id1)
    }

    db_session.add(Poker(id=fake_poker_id1, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id1, poker_id=fake_poker_id1, name="Story 1"))
    db_session.add(Participant(id=fake_participant_id, poker_id=fake_poker_id1, name="Arthur", sid=fake_sid))
    db_session.commit()

    def fake_query_participants(*args, **kwargs):
        return []

    service = worker_factory(EventService, db=db_session)
    service.participant_rpc.query.side_effect = fake_query_participants
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(NotFound):
        result = service.create(fake_sid, fake_payload)


def test_when_creating_system_event_should_return_dict_with_system_creator(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id1 = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_participant_id = uuid.uuid4()

    fake_payload = {
        "type": "vote",
        "content": "5",
        "revealed": "false",
        "story_id": str(fake_story_id1)
    }

    db_session.add(Poker(id=fake_poker_id1, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id1, poker_id=fake_poker_id1, name="Story 1"))
    db_session.add(Participant(id=fake_participant_id, poker_id=fake_poker_id1, name="Arthur", sid=fake_sid))
    db_session.commit()

    def fake_query_participants(*args, **kwargs):
        return []

    service = worker_factory(EventService, db=db_session)
    service.participant_rpc.query.side_effect = fake_query_participants
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.create(fake_sid, fake_payload, _system_event=True)

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert 'type' in result
    assert 'content' in result
    assert 'storyId' in result
    assert 'revealed' in result
    assert 'creator' in result
    assert result['id'] is not None
    assert result['type'] == "vote"
    assert result['content'] == "5"
    assert result['revealed'] is False
    assert result['storyId'] == str(fake_story_id1)
    assert result['creator'] == "system"
    service.gateway_rpc.broadcast.assert_called_once()
    service.dispatch.assert_called_once()
