import uuid

import pytest
from nameko.testing.services import worker_factory
from pydantic import ValidationError

from base.exceptions import NotFound, InvalidFilter
from poker.models import Poker
from story.models import Story
from polling.models import Polling
from polling.service import PollingService
from participant.models import Participant
from event.models import Event


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
    service.gateway_rpc.unicast.assert_called_once()
    service.dispatch.assert_called_once()
