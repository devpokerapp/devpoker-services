import uuid

import pytest
from nameko.testing.services import worker_factory
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from base.exceptions import NotFound, InvalidFilter, InvalidInput
from poker.models import Poker
from story.models import Story
from polling.models import Polling
from vote.models import Vote
from event.models import Event
from participant.models import Participant
from vote.service import VoteService


def test_when_retrieving_vote_should_return_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_participant_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()
    fake_polling_id = uuid.uuid4()
    fake_vote_id = uuid.uuid4()

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id, name="Story 1", poker_id=fake_poker_id))
    db_session.add(Participant(id=fake_participant_id, poker_id=fake_poker_id, name="Arthur", sid=fake_sid))
    db_session.commit()
    db_session.add(Polling(id=fake_polling_id, story_id=fake_story_id, poker_id=fake_poker_id))
    db_session.commit()
    db_session.add(Vote(id=fake_vote_id, value="?", polling_id=fake_polling_id, participant_id=fake_participant_id,
                        poker_id=fake_poker_id))
    db_session.commit()

    service = worker_factory(VoteService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.retrieve(fake_sid, str(fake_vote_id))

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    assert 'pollingId' in result
    assert result['pollingId'] == str(fake_polling_id)
    assert 'participantId' in result
    assert result['participantId'] == str(fake_participant_id)
    assert 'value' in result
    assert result['value'] == "?"
    assert 'participant' in result
    assert type(result['participant']) is dict
    service.gateway_rpc.unicast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_placing_vote_should_return_new_vote_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_participant_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()
    fake_polling_id = uuid.uuid4()

    fake_payload = {
        "value": "1",
        "pollingId": str(fake_polling_id)
    }

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id, name="Story 1", poker_id=fake_poker_id))
    db_session.add(Participant(id=fake_participant_id, poker_id=fake_poker_id, name="Arthur", sid=fake_sid))
    db_session.commit()
    db_session.add(Polling(id=fake_polling_id, story_id=fake_story_id, poker_id=fake_poker_id))
    db_session.commit()

    def fake_participant_current(*args, **kwargs):
        return {
            "id": str(fake_participant_id),
            "name": "Arthur",
            "sid": fake_sid,
            "poker_id": str(fake_poker_id),
        }

    def fake_polling_retrieve(*args, **kwargs):
        return {
            "id": str(fake_polling_id),
            "value": "5",
            "revealed": True,
            "completed": False,
            "storyId": str(fake_story_id)
        }

    service = worker_factory(VoteService, db=db_session)
    service.participant_rpc.current.side_effect = fake_participant_current
    service.polling_rpc.retrieve.side_effect = fake_polling_retrieve
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.place(fake_sid, fake_payload)

    # assert
    assert 'id' in result
    assert result['id'] is not None
    assert 'value' in result
    assert 'pollingId' in result
    assert 'participantId' in result
    assert 'participant' in result
    service.gateway_rpc.broadcast.assert_called()
    service.dispatch.assert_called()


def test_when_placing_vote_again_should_return_updated_vote_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_participant_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()
    fake_polling_id = uuid.uuid4()
    fake_vote_id = uuid.uuid4()

    fake_payload = {
        "value": "1",
        "pollingId": str(fake_polling_id)
    }

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id, name="Story 1", poker_id=fake_poker_id))
    db_session.add(Participant(id=fake_participant_id, poker_id=fake_poker_id, name="Arthur", sid=fake_sid))
    db_session.commit()
    db_session.add(Polling(id=fake_polling_id, story_id=fake_story_id, poker_id=fake_poker_id))
    db_session.commit()
    db_session.add(Vote(id=fake_vote_id, value="?", polling_id=fake_polling_id, participant_id=fake_participant_id,
                        poker_id=fake_poker_id))
    db_session.commit()

    def fake_participant_current(*args, **kwargs):
        return {
            "id": str(fake_participant_id),
            "name": "Arthur",
            "sid": fake_sid,
            "poker_id": str(fake_poker_id),
        }

    def fake_polling_retrieve(*args, **kwargs):
        return {
            "id": str(fake_polling_id),
            "value": "5",
            "revealed": True,
            "completed": False,
            "storyId": str(fake_story_id)
        }

    service = worker_factory(VoteService, db=db_session)
    service.participant_rpc.current.side_effect = fake_participant_current
    service.polling_rpc.retrieve.side_effect = fake_polling_retrieve
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.place(fake_sid, fake_payload)

    # assert
    assert 'id' in result
    assert result['id'] == str(fake_vote_id)
    assert 'value' in result
    assert result['value'] == "1"
    assert 'pollingId' in result
    assert 'participantId' in result
    assert 'participant' in result
    service.gateway_rpc.broadcast.assert_called()
    service.dispatch.assert_called()


def test_when_placing_vote_on_non_existing_polling_should_cause_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_participant_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()
    non_existing_polling_id = uuid.uuid4()

    fake_payload = {
        "value": "1",
        "pollingId": str(non_existing_polling_id)
    }

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id, name="Story 1", poker_id=fake_poker_id))
    db_session.add(Participant(id=fake_participant_id, poker_id=fake_poker_id, name="Arthur", sid=fake_sid))
    db_session.commit()

    def fake_participant_current(*args, **kwargs):
        return {
            "id": str(fake_participant_id),
            "name": "Arthur",
            "sid": fake_sid,
            "poker_id": str(fake_poker_id),
        }

    def fake_polling_retrieve(*args, **kwargs):
        raise NotFound()

    service = worker_factory(VoteService, db=db_session)
    service.participant_rpc.current.side_effect = fake_participant_current
    service.polling_rpc.retrieve.side_effect = fake_polling_retrieve
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(NotFound):
        result = service.place(fake_sid, fake_payload)


def test_when_placing_vote_on_completed_polling_should_cause_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_participant_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()
    fake_polling_id = uuid.uuid4()

    fake_payload = {
        "value": "1",
        "pollingId": str(fake_polling_id)
    }

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id, name="Story 1", poker_id=fake_poker_id))
    db_session.add(Participant(id=fake_participant_id, poker_id=fake_poker_id, name="Arthur", sid=fake_sid))
    db_session.commit()
    db_session.add(Polling(id=fake_polling_id, revealed=True, completed=True, story_id=fake_story_id,
                           poker_id=fake_poker_id))
    db_session.commit()

    def fake_participant_current(*args, **kwargs):
        return {
            "id": str(fake_participant_id),
            "name": "Arthur",
            "sid": fake_sid,
            "poker_id": str(fake_poker_id),
        }

    def fake_polling_retrieve(*args, **kwargs):
        return {
            "id": str(fake_polling_id),
            "value": "5",
            "revealed": True,
            "completed": True,
            "storyId": str(fake_story_id)
        }

    service = worker_factory(VoteService, db=db_session)
    service.participant_rpc.current.side_effect = fake_participant_current
    service.polling_rpc.retrieve.side_effect = fake_polling_retrieve
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(InvalidInput):
        result = service.place(fake_sid, fake_payload)


def test_when_placing_vote_should_get_poker_id_from_polling(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_participant_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()
    fake_polling_id = uuid.uuid4()

    fake_payload = {
        "value": "1",
        "pollingId": str(fake_polling_id)
    }

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id, name="Story 1", poker_id=fake_poker_id))
    db_session.add(Participant(id=fake_participant_id, poker_id=fake_poker_id, name="Arthur", sid=fake_sid))
    db_session.commit()
    db_session.add(Polling(id=fake_polling_id, story_id=fake_story_id, poker_id=fake_poker_id))
    db_session.commit()

    def fake_participant_current(*args, **kwargs):
        return {
            "id": str(fake_participant_id),
            "name": "Arthur",
            "sid": fake_sid,
            "poker_id": str(fake_poker_id),
        }

    def fake_polling_retrieve(*args, **kwargs):
        return {
            "id": str(fake_polling_id),
            "value": "5",
            "revealed": True,
            "completed": False,
            "storyId": str(fake_story_id),
            "pokerId": str(fake_poker_id)
        }

    service = worker_factory(VoteService, db=db_session)
    service.participant_rpc.current.side_effect = fake_participant_current
    service.polling_rpc.retrieve.side_effect = fake_polling_retrieve
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.place(fake_sid, fake_payload)

    # assert
    assert 'id' in result
    assert result['id'] is not None
    assert 'value' in result
    assert 'pollingId' in result
    assert 'participantId' in result
    assert 'participant' in result
    assert 'pokerId' in result
    assert result['pokerId'] is not None
    assert result['pokerId'] == str(fake_poker_id)
    service.gateway_rpc.broadcast.assert_called()
    service.dispatch.assert_called()
