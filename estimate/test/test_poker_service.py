import pytest
import uuid
from nameko.testing.services import worker_factory
from pydantic import ValidationError
from base.exceptions import NotFound
from poker.service import PokerService
from poker.models import Poker


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


def test_when_retrieving_poker_should_return_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_entity_id = uuid.uuid4()

    db_session.add(Poker(id=fake_entity_id, creator='user@test.com'))
    db_session.commit()

    service = worker_factory(PokerService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.retrieve(fake_sid, fake_entity_id)

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    service.gateway_rpc.unicast.assert_called_once()


def test_when_retrieving_non_existing_poker_should_return_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_entity_id = uuid.uuid4()

    service = worker_factory(PokerService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(NotFound):
        result = service.retrieve(fake_sid, fake_entity_id)
