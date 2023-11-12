import uuid

import pytest
from nameko.testing.services import worker_factory
from pydantic import ValidationError

from base.exceptions import NotFound
from participant.models import Participant
from participant.service import ParticipantService


def test_when_creating_participant_should_return_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_payload = {
        'sid': fake_sid,
        'name': 'Arthur',
        'pokerId': str(fake_poker_id)
    }

    service = worker_factory(ParticipantService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.create(fake_sid, fake_payload)

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    assert 'name' in result
    assert type(result['name']) is str
    assert result['name'] == 'Arthur'
    assert 'pokerId' in result
    assert type(result['pokerId']) is str
    assert result['pokerId'] == str(fake_poker_id)
    service.gateway_rpc.unicast.assert_called_once()
    service.dispatch.assert_called_once()