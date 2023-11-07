import uuid

import pytest
from nameko.testing.services import worker_factory
from pydantic import ValidationError

from base.exceptions import NotFound
from poker.models import Poker
from story.models import Story
from story.service import StoryService


def test_when_creating_story_should_return_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_payload = {
        'name': 'Story 1',
        'pokerId': str(fake_poker_id)
    }

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.create(fake_sid, fake_payload)

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    assert 'pokerId' in result
    assert type(result['pokerId']) is str
    assert result['pokerId'] == str(fake_poker_id)
    service.gateway_rpc.unicast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_creating_story_without_name_should_cause_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_payload = {
        'pokerId': str(fake_poker_id)
    }

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(ValidationError):
        result = service.create(fake_sid, fake_payload)


def test_when_retrieving_story_should_return_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id, name="Story 1", poker_id=fake_poker_id))
    db_session.commit()

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.retrieve(fake_sid, str(fake_story_id))

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    service.gateway_rpc.unicast.assert_called_once()


def test_when_retrieving_non_existing_story_should_return_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_entity_id = uuid.uuid4()

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(NotFound):
        result = service.retrieve(fake_sid, str(fake_entity_id))


def test_when_retrieving_story_with_non_uuid_string_should_return_value_error(db_session):
    # arrange
    fake_sid = '1aaa'
    confused_entity_id = 'arthur'

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(ValueError):
        result = service.retrieve(fake_sid, str(confused_entity_id))


def test_when_updating_story_should_return_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()
    fake_payload = {
        'id': str(fake_story_id),
        'name': 'Revised Story 1',
        'pokerId': str(fake_poker_id)
    }

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id, name="Story 1", poker_id=fake_poker_id))
    db_session.commit()

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.update(fake_sid, str(fake_story_id), fake_payload)

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    assert 'name' in result
    assert type(result['name']) is str
    assert result['name'] == "Revised Story 1"
    assert 'pokerId' in result
    assert type(result['pokerId']) is str
    assert result['pokerId'] == str(fake_poker_id)
    service.gateway_rpc.unicast.assert_called_once()


def test_when_updating_non_existing_story_should_cause_not_found_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()
    fake_payload = {
        'id': str(fake_story_id),
        'name': 'Revised Story 1',
        'storyId': str(fake_poker_id)
    }

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(NotFound):
        result = service.update(fake_sid, str(fake_story_id), fake_payload)


def test_when_updating_story_with_non_uuid_string_should_cause_value_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_story_id = 'arthur'
    fake_payload = {
        'id': str(fake_story_id),
        'name': 'Revised Story 1',
        'storyId': str(fake_poker_id)
    }

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(ValueError):
        result = service.update(fake_sid, str(fake_story_id), fake_payload)
