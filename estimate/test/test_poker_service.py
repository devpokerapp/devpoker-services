import pytest
from nameko.testing.services import worker_factory
from pydantic import ValidationError
from poker.service import PokerService
from poker.models import Poker
from story.models import Story


def test_when_creating_poker_should_return_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_payload = {
        'creator': 'user@test.com'
    }

    service = worker_factory(PokerService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.create(fake_sid, fake_payload)

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    service.gateway_rpc.unicast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_creating_poker_without_creator_should_cause_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_payload = {}

    service = worker_factory(PokerService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(ValidationError):
        result = service.create(fake_sid, fake_payload)

