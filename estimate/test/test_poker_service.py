import pytest
import uuid
from nameko.testing.services import worker_factory
from pydantic import ValidationError
from base.exceptions import NotFound
from poker.service import PokerService
from poker.models import Poker
from participant.models import Participant
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
    assert 'stories' in result
    assert type(result['stories']) is list
    assert 'participants' in result
    assert type(result['participants']) is list
    service.gateway_rpc.broadcast.assert_called_once()
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
    service.gateway_rpc.get_current_poker_id.side_effect = lambda *args, **kwargs: fake_entity_id
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.retrieve(fake_sid, str(fake_entity_id))

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    assert 'stories' in result
    assert type(result['stories']) is list
    assert 'participants' in result
    assert type(result['participants']) is list
    service.gateway_rpc.unicast.assert_called_once()


def test_when_retrieving_non_existing_poker_should_return_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_entity_id = uuid.uuid4()

    service = worker_factory(PokerService, db=db_session)
    service.gateway_rpc.get_current_poker_id.side_effect = lambda *args, **kwargs: None
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(NotFound):
        result = service.retrieve(fake_sid, str(fake_entity_id))


def test_when_selecting_story_should_return_story_dict(db_session, monkeypatch):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()
    fake_story = {
        'id': str(fake_story_id),
        'poker_id': str(fake_poker_id),
    }

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id, name="Story 1", poker_id=fake_poker_id))
    db_session.commit()

    service = worker_factory(PokerService, db=db_session)
    service.story_rpc.retrieve.side_effect = lambda *args, **kwargs: fake_story
    service.gateway_rpc.get_current_poker_id.side_effect = lambda *args, **kwargs: fake_poker_id
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.select_story(sid=fake_sid, poker_id=str(fake_poker_id), story_id=str(fake_story_id))

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    assert result['id'] == str(fake_story_id)
    service.gateway_rpc.broadcast.assert_called()
    service.dispatch.assert_called()


def test_when_selecting_non_existing_story_should_cause_error(db_session, monkeypatch):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()

    def fake_story_retrieve(*args, **kwargs):
        raise NotFound()

    service = worker_factory(PokerService, db=db_session)
    service.story_rpc.retrieve.side_effect = fake_story_retrieve
    service.gateway_rpc.get_current_poker_id.side_effect = lambda *args, **kwargs: fake_poker_id
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(NotFound):
        result = service.select_story(sid=fake_sid, poker_id=str(fake_poker_id), story_id=str(fake_story_id))


def test_when_selecting_story_with_none_should_unselect(db_session, monkeypatch):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()

    service = worker_factory(PokerService, db=db_session)
    service.story_rpc.retrieve.side_effect = lambda *args, **kwargs: None
    service.gateway_rpc.get_current_poker_id.side_effect = lambda *args, **kwargs: fake_poker_id
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.select_story(sid=fake_sid, poker_id=str(fake_poker_id), story_id=None)

    # assert
    assert result is None
    service.gateway_rpc.broadcast.assert_called()
    service.dispatch.assert_called()


def test_when_retrieving_poker_without_being_participant_should_return_not_found(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_entity_id = uuid.uuid4()
    fake_wrong_entity_id = uuid.uuid4()

    db_session.add(Poker(id=fake_entity_id, creator='user@test.com'))
    db_session.commit()

    def fake_get_current_poker_id(*args, **kwargs):
        return fake_wrong_entity_id

    service = worker_factory(PokerService, db=db_session)
    service.gateway_rpc.get_current_poker_id.side_effect = fake_get_current_poker_id
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(NotFound):
        result = service.retrieve(fake_sid, str(fake_entity_id))
