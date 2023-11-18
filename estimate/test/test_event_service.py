import uuid

import pytest
from nameko.testing.services import worker_factory
from pydantic import ValidationError

from base.exceptions import NotFound, InvalidFilter
from poker.models import Poker
from story.models import Story
from event.models import Event
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


def test_when_creating_event_should_return_as_dict(db_session):
    pass


def test_when_creating_event_with_invalid_type_should_cause_error(db_session):
    pass
