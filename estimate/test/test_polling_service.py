import uuid

import pytest
from nameko.testing.services import worker_factory

from poker.models import Poker
from story.models import Story
from polling.models import Polling
from polling.service import PollingService


def test_when_retrieving_polling_should_return_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()
    fake_polling_id = uuid.uuid4()

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id, name="Story 1", poker_id=fake_poker_id))
    db_session.commit()
    db_session.add(Polling(id=fake_polling_id, story_id=fake_story_id))
    db_session.commit()

    service = worker_factory(PollingService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.retrieve(fake_sid, str(fake_polling_id))

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    assert 'storyId' in result
    assert type(result['storyId']) is str
    assert result['storyId'] == str(fake_story_id)
    assert 'votes' in result
    assert type(result['votes']) is list
    assert 'value' in result
    assert result['value'] is None
    assert 'completed' in result
    assert result['completed'] is False
    assert 'revealed' in result
    assert result['revealed'] is False
    service.gateway_rpc.unicast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_getting_current_polling_should_return_last_not_completed_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()
    fake_polling_id_completed = uuid.uuid4()
    fake_polling_id_opened1 = uuid.uuid4()
    fake_polling_id_opened2 = uuid.uuid4()
    fake_polling_id_current = uuid.uuid4()

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id, name="Story 1", poker_id=fake_poker_id))
    db_session.commit()
    db_session.add(Polling(id=fake_polling_id_completed, story_id=fake_story_id, completed=True, revealed=True))
    db_session.add(Polling(id=fake_polling_id_opened1, story_id=fake_story_id, completed=False, revealed=True))
    db_session.add(Polling(id=fake_polling_id_opened2, story_id=fake_story_id, completed=False, revealed=True))
    db_session.add(Polling(id=fake_polling_id_current, story_id=fake_story_id, completed=False, revealed=True))
    db_session.commit()

    service = worker_factory(PollingService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.current(fake_sid, str(fake_story_id))

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    assert result['id'] == str(fake_polling_id_current)
    assert 'storyId' in result
    assert type(result['storyId']) is str
    assert result['storyId'] == str(fake_story_id)
    assert 'votes' in result
    assert type(result['votes']) is list
    assert 'value' in result
    assert result['value'] is None
    assert 'completed' in result
    assert result['completed'] is False
    assert 'revealed' in result
    assert result['revealed'] is True
    service.gateway_rpc.unicast.assert_not_called()
    service.dispatch.assert_not_called()
