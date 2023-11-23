import pytest
import uuid
from nameko.testing.services import worker_factory
from pydantic import ValidationError
from base.exceptions import NotFound
from poker.service import PokerService
from poker.models import Poker
from participant.models import Participant


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
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(NotFound):
        result = service.retrieve(fake_sid, str(fake_entity_id))


def test_when_joining_poker_should_subscribe_to_room(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_participant_id = uuid.uuid4()
    fake_participant = {
        'id': str(fake_participant_id)
    }

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Participant(id=fake_participant_id, poker_id=fake_poker_id, name="Arthur", sid="2aaa"))
    db_session.commit()

    service = worker_factory(PokerService, db=db_session)
    service.participant_rpc.retrieve.side_effect = lambda *args, **kwargs: fake_participant
    service.participant_rpc.update.side_effect = lambda *args, **kwargs: None
    service.gateway_rpc.subscribe.side_effect = lambda *args, **kwargs: None
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.join(fake_sid, participant_id=str(fake_participant_id), poker_id=str(fake_poker_id))

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    assert result['id'] == str(fake_participant_id)  # defined in fake_participant
    service.participant_rpc.retrieve.assert_called_once()
    service.participant_rpc.update.assert_called_once()
    service.gateway_rpc.subscribe.assert_called_once()
    service.gateway_rpc.broadcast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_joining_non_existing_user_in_poker_should_cause_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_participant_id = uuid.uuid4()

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Participant(id=fake_participant_id, poker_id=fake_poker_id, name="Arthur", sid="2aaa"))
    db_session.commit()

    def fake_participant_retrieve(*args, **kwargs):
        raise NotFound()

    service = worker_factory(PokerService, db=db_session)
    service.participant_rpc.retrieve.side_effect = fake_participant_retrieve
    service.gateway_rpc.subscribe.side_effect = lambda *args, **kwargs: None
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(NotFound):
        result = service.join(fake_sid, participant_id=str(fake_participant_id), poker_id=str(fake_poker_id))


def test_when_getting_poker_context_should_return_as_dict(db_session, monkeypatch):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_poker = {
        'id': str(fake_poker_id)
    }
    fake_query_response = {
        "items": [],
        "metadata": {
            "filters": []
        }
    }

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()

    service = worker_factory(PokerService, db=db_session)
    service.story_rpc.query.side_effect = lambda *args, **kwargs: fake_query_response
    service.participant_rpc.query.side_effect = lambda *args, **kwargs: fake_query_response
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    monkeypatch.setattr(service, 'retrieve', lambda *args, **kwargs: fake_poker)

    # act
    result = service.context(sid=fake_sid, entity_id=str(fake_poker_id))

    # assert
    assert type(result) is dict
    assert 'poker' in result
    assert 'stories' in result
    assert 'participants' in result
    assert type(result['poker']) is dict
    assert type(result['stories']) is list
    assert type(result['participants']) is list
    service.gateway_rpc.unicast.assert_called_once()


def test_when_getting_poker_context_from_non_existing_should_cause_error(db_session, monkeypatch):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_poker = {
        'id': str(fake_poker_id)
    }
    fake_query_response = {
        "items": [],
        "metadata": {
            "filters": []
        }
    }

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()

    def fake_poker_retrieve(*args, **kwargs):
        raise NotFound()

    service = worker_factory(PokerService, db=db_session)
    service.story_rpc.query.side_effect = lambda *args, **kwargs: fake_query_response
    service.participant_rpc.query.side_effect = lambda *args, **kwargs: fake_query_response
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    monkeypatch.setattr(service, 'retrieve', fake_poker_retrieve)

    # act
    # assert
    with pytest.raises(NotFound):
        result = service.context(sid=fake_sid, entity_id=str(fake_poker_id))


def test_when_selecting_story_should_return_story_dict(db_session, monkeypatch):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()
    fake_story = {
        'id': str(fake_story_id),
        'poker_id': str(fake_poker_id),
    }

    def fake_poker_retrieve(*args, **kwargs):
        return {
            'id': str(fake_poker_id),
            'creator': 'user@test.com',
            'current_story_id': None
        }

    def fake_poker_update(*args, **kwargs):
        pass

    service = worker_factory(PokerService, db=db_session)
    service.story_rpc.retrieve.side_effect = lambda *args, **kwargs: fake_story
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    monkeypatch.setattr(service, 'retrieve', fake_poker_retrieve)
    monkeypatch.setattr(service, 'update', fake_poker_update)

    # act
    result = service.select_story(sid=fake_sid, poker_id=str(fake_poker_id), story_id=str(fake_story_id))

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    assert result['id'] == str(fake_story_id)
    service.gateway_rpc.broadcast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_selecting_non_existing_story_should_cause_error(db_session, monkeypatch):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()

    def fake_poker_retrieve(*args, **kwargs):
        pass

    def fake_poker_update(*args, **kwargs):
        pass

    def fake_story_retrieve(*args, **kwargs):
        raise NotFound()

    service = worker_factory(PokerService, db=db_session)
    service.story_rpc.retrieve.side_effect = fake_story_retrieve
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    monkeypatch.setattr(service, 'retrieve', fake_poker_retrieve)
    monkeypatch.setattr(service, 'update', fake_poker_update)

    # act
    # assert
    with pytest.raises(NotFound):
        result = service.select_story(sid=fake_sid, poker_id=str(fake_poker_id), story_id=str(fake_story_id))


def test_when_selecting_story_with_none_should_unselect(db_session, monkeypatch):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()

    def fake_poker_retrieve(*args, **kwargs):
        return {
            'id': str(fake_poker_id),
            'creator': 'user@test.com',
            'current_story_id': None
        }

    def fake_poker_update(*args, **kwargs):
        pass

    service = worker_factory(PokerService, db=db_session)
    service.story_rpc.retrieve.side_effect = lambda *args, **kwargs: None
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    monkeypatch.setattr(service, 'retrieve', fake_poker_retrieve)
    monkeypatch.setattr(service, 'update', fake_poker_update)

    # act
    result = service.select_story(sid=fake_sid, poker_id=str(fake_poker_id), story_id=None)

    # assert
    assert result is None
    service.gateway_rpc.broadcast.assert_called_once()
    service.dispatch.assert_called_once()
