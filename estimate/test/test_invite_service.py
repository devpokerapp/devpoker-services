import uuid

import pytest
from nameko.testing.services import worker_factory
from pydantic import ValidationError

from base.exceptions import NotFound
from invite.models import Invite
from invite.service import InviteService

def test_when_creating_invite_should_return_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_payload = {
        'expiresAt': '2024-03-16 10:46:08',
        'pokerId': str(fake_poker_id)
    }
    
    service = worker_factory(InviteService, db=db_session)
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.create(fake_sid, fake_payload)
    
    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    service.gateway_rpc.broadcast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_creating_invite_with_code_should_ignore_and_generate_fixed_size_string(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_code_to_be_ignored = 'foobarbazfoobarbazfoobarbaz'
    fake_payload = {
        'expiresAt': '2024-03-16 10:46:08',
        'pokerId': str(fake_poker_id),
        'code': fake_code_to_be_ignored
    }
    
    service = worker_factory(InviteService, db=db_session)
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.create(fake_sid, fake_payload)
    
    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    assert 'code' in result
    assert type(result['code']) is str
    assert not result['code'] == fake_code_to_be_ignored
    assert len(result['code']) == 48
    service.gateway_rpc.broadcast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_creating_invite_with_code_should_be_different_from_last_one(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_code_to_be_ignored = 'foobarbazfoobarbazfoobarbaz'
    fake_payload = {
        'expiresAt': '2024-03-16 10:46:08',
        'pokerId': str(fake_poker_id),
        'code': fake_code_to_be_ignored
    }
    
    service = worker_factory(InviteService, db=db_session)
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    first_result = service.create(fake_sid, fake_payload)
    second_result = service.create(fake_sid, fake_payload)
    
    # assert
    assert type(first_result) is dict
    assert type(second_result) is dict
    assert 'code' in first_result
    assert 'code' in second_result
    assert first_result['code'] != second_result['code']
