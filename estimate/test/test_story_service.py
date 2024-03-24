import uuid

import pytest
from nameko.testing.services import worker_factory
from pydantic import ValidationError

from base.exceptions import NotFound, InvalidFilter
from poker.models import Poker
from story.models import Story
from story.service import StoryService
from participant.models import Participant
from event.models import Event


def test_when_creating_story_should_return_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_payload = {
        'name': 'Story 1',
        'pokerId': str(fake_poker_id)
    }

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
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
    assert 'events' in result
    assert type(result['events']) is list
    service.gateway_rpc.broadcast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_creating_story_without_name_should_cause_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_payload = {
        'pokerId': str(fake_poker_id)
    }

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
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
    service.gateway_rpc.get_current_poker_id.side_effect = lambda *args, **kwargs: fake_poker_id
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.retrieve(fake_sid, str(fake_story_id))

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    assert 'events' in result
    assert type(result['events']) is list
    assert 'pollings' in result
    assert type(result['pollings']) is list
    service.gateway_rpc.unicast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_retrieving_non_existing_story_should_return_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_entity_id = uuid.uuid4()
    fake_poker_id = uuid.uuid4()

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.get_current_poker_id.side_effect = lambda *args, **kwargs: fake_poker_id
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
    service.gateway_rpc.get_current_poker_id.side_effect = lambda *args, **kwargs: fake_poker_id
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
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
    assert 'events' in result
    assert type(result['events']) is list
    service.gateway_rpc.broadcast.assert_called_once()
    service.dispatch.assert_called_once()


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
    service.gateway_rpc.get_current_poker_id.side_effect = lambda *args, **kwargs: fake_poker_id
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
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
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(ValueError):
        result = service.update(fake_sid, str(fake_story_id), fake_payload)


def test_when_deleting_story_should_return_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id, name="Story 1", poker_id=fake_poker_id))
    db_session.commit()

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.get_current_poker_id.side_effect = lambda *args, **kwargs: fake_poker_id
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.delete(fake_sid, str(fake_story_id))

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    assert 'name' in result
    assert type(result['name']) is str
    assert result['name'] == "Story 1"
    assert 'pokerId' in result
    assert type(result['pokerId']) is str
    assert result['pokerId'] == str(fake_poker_id)
    assert 'events' in result
    assert type(result['events']) is list
    service.gateway_rpc.broadcast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_deleting_non_existing_story_should_cause_not_found_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.get_current_poker_id.side_effect = lambda *args, **kwargs: fake_poker_id
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(NotFound):
        result = service.delete(fake_sid, str(fake_story_id))


def test_when_deleting_story_with_non_uuid_string_should_cause_value_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_story_id = 'arthur'

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(ValueError):
        result = service.delete(fake_sid, str(fake_story_id))


def test_when_querying_stories_should_return_as_dict_with_list(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_story_id2 = uuid.uuid4()

    fake_filters = []

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id1, name="Story 1", poker_id=fake_poker_id))
    db_session.commit()
    db_session.add(Story(id=fake_story_id2, name="Story 2", poker_id=fake_poker_id))
    db_session.commit()

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.get_current_poker_id.side_effect = lambda *args, **kwargs: fake_poker_id
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.query(fake_sid, fake_filters)

    # assert
    assert type(result) is dict
    assert 'items' in result
    assert 'metadata' in result
    assert type(result['items']) is list
    assert type(result['metadata']) is dict
    assert len(result['items']) == 2
    assert 'id' in result['items'][0]
    assert result['items'][0]['id'] == str(fake_story_id1)
    assert 'filters' in result['metadata']
    assert type(result['metadata']['filters']) is list
    assert len(result['metadata']['filters']) == len(fake_filters)
    service.gateway_rpc.unicast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_querying_stories_with_same_poker_id_should_return_only_stories_related_to_that_poker(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id1 = uuid.uuid4()
    fake_poker_id2 = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_story_id2 = uuid.uuid4()
    fake_story_id3 = uuid.uuid4()

    fake_filters = [
        {
            "attr": 'poker_id',
            "value": str(fake_poker_id1)
        }
    ]

    db_session.add(Poker(id=fake_poker_id1, creator='user@test.com'))
    db_session.add(Poker(id=fake_poker_id2, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id1, name="Story 1", poker_id=fake_poker_id1))
    db_session.add(Story(id=fake_story_id2, name="Story 2", poker_id=fake_poker_id1))
    db_session.add(Story(id=fake_story_id3, name="Story from other poker", poker_id=fake_poker_id2))
    db_session.commit()

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.get_current_poker_id.side_effect = lambda *args, **kwargs: fake_poker_id1
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.query(fake_sid, fake_filters)

    # assert
    assert type(result) is dict
    assert 'items' in result
    assert 'metadata' in result
    assert type(result['items']) is list
    assert type(result['metadata']) is dict
    assert len(result['items']) == 2
    assert 'id' in result['items'][0]
    assert result['items'][0]['id'] == str(fake_story_id1)
    assert 'id' in result['items'][1]
    assert result['items'][1]['id'] == str(fake_story_id2)
    assert 'events' in result['items'][1]
    assert type(result['items'][1]['events']) is list
    assert 'filters' in result['metadata']
    assert type(result['metadata']['filters']) is list
    assert len(result['metadata']['filters']) == len(fake_filters)
    assert type(result['metadata']['filters'][0]) is dict
    assert 'attr' in result['metadata']['filters'][0]
    assert 'value' in result['metadata']['filters'][0]
    assert type(result['metadata']['filters'][0]['attr']) is str
    assert type(result['metadata']['filters'][0]['value']) is str
    assert result['metadata']['filters'][0]['attr'] == 'poker_id'
    assert result['metadata']['filters'][0]['value'] == str(fake_poker_id1)
    service.gateway_rpc.unicast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_querying_stories_from_poker_id_without_stories_should_return_empty_list(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id1 = uuid.uuid4()

    fake_filters = [
        {
            "attr": 'poker_id',
            "value": str(fake_poker_id1)
        }
    ]

    db_session.add(Poker(id=fake_poker_id1, creator='user@test.com'))
    db_session.commit()

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.get_current_poker_id.side_effect = lambda *args, **kwargs: fake_poker_id1
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.query(fake_sid, fake_filters)

    # assert
    assert type(result) is dict
    assert 'items' in result
    assert 'metadata' in result
    assert type(result['items']) is list
    assert type(result['metadata']) is dict
    assert len(result['items']) == 0
    assert 'filters' in result['metadata']
    assert type(result['metadata']['filters']) is list
    assert len(result['metadata']['filters']) == len(fake_filters)
    service.gateway_rpc.unicast.assert_called_once()
    service.dispatch.assert_called_once()


def test_when_querying_stories_with_invalid_value_should_cause_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id1 = uuid.uuid4()
    fake_poker_id2 = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_story_id2 = uuid.uuid4()
    fake_story_id3 = uuid.uuid4()

    fake_filters = [
        {
            "attr": 'poker_id',
            "value": ''
        }
    ]

    db_session.add(Poker(id=fake_poker_id1, creator='user@test.com'))
    db_session.add(Poker(id=fake_poker_id2, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id1, name="Story 1", poker_id=fake_poker_id1))
    db_session.add(Story(id=fake_story_id2, name="Story 2", poker_id=fake_poker_id1))
    db_session.add(Story(id=fake_story_id3, name="Story from other poker", poker_id=fake_poker_id2))
    db_session.commit()

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(InvalidFilter):
        result = service.query(fake_sid, fake_filters)


def test_when_querying_stories_with_non_allowed_filter_should_cause_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id1 = uuid.uuid4()
    fake_poker_id2 = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_story_id2 = uuid.uuid4()
    fake_story_id3 = uuid.uuid4()

    fake_filters = [
        {
            "attr": 'fake_field',
            "value": ''
        }
    ]

    db_session.add(Poker(id=fake_poker_id1, creator='user@test.com'))
    db_session.add(Poker(id=fake_poker_id2, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id1, name="Story 1", poker_id=fake_poker_id1))
    db_session.add(Story(id=fake_story_id2, name="Story 2", poker_id=fake_poker_id1))
    db_session.add(Story(id=fake_story_id3, name="Story from other poker", poker_id=fake_poker_id2))
    db_session.commit()

    service = worker_factory(StoryService, db=db_session)
    service.gateway_rpc.unicast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(InvalidFilter):
        result = service.query(fake_sid, fake_filters)


def test_when_revealing_votes_for_story_should_return_story_as_dict(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id1 = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_event_id1 = uuid.uuid4()
    fake_event_id2 = uuid.uuid4()
    fake_participant_id1 = uuid.uuid4()
    fake_participant_id2 = uuid.uuid4()

    db_session.add(Poker(id=fake_poker_id1, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id1, name="Story 1", poker_id=fake_poker_id1))
    db_session.add(Participant(id=fake_participant_id1, poker_id=fake_poker_id1, name="Arthur", sid=fake_sid))
    db_session.add(Participant(id=fake_participant_id2, poker_id=fake_poker_id1, name="Bruno", sid=fake_sid))
    db_session.commit()
    db_session.add(Event(id=fake_event_id1, type="vote", content="5", revealed=False, creator=str(fake_participant_id1),
                         story_id=fake_story_id1, poker_id=fake_poker_id1))
    db_session.add(Event(id=fake_event_id2, type="vote", content="2", revealed=False, creator=str(fake_participant_id2),
                         story_id=fake_story_id1, poker_id=fake_poker_id1))
    db_session.commit()

    def fake_event_query(*args, **kwargs):
        return {
            "items": [
                {
                    "id": str(fake_event_id1),
                    "type": "vote",
                    "content": "5",
                    "revealed": False,
                    "creator": str(fake_participant_id1),
                    "storyId": str(fake_story_id1)
                },
                {
                    "id": str(fake_event_id2),
                    "type": "vote",
                    "content": "2",
                    "revealed": False,
                    "creator": str(fake_participant_id1),
                    "storyId": str(fake_story_id1)
                }
            ]
        }

    def fake_event_update(*args, **kwargs):
        return {
            "id": str(fake_event_id1),
            "type": "vote",
            "content": "5",
            "revealed": True,
            "creator": str(fake_participant_id1),
            "storyId": str(fake_story_id1)
        }

    service = worker_factory(StoryService, db=db_session)
    service.event_rpc.query.side_effect = fake_event_query
    service.event_rpc.update.side_effect = fake_event_update
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    result = service.reveal(fake_sid, str(fake_story_id1))

    # assert
    assert type(result) is dict
    assert 'id' in result
    assert type(result['id']) is str
    assert 'pokerId' in result
    assert type(result['pokerId']) is str
    assert result['pokerId'] == str(fake_poker_id1)
    assert 'events' in result
    assert type(result['events']) is list
    assert len(result['events']) == 2
    service.gateway_rpc.broadcast.assert_called_once()
    service.dispatch.assert_called_once()
    service.event_rpc.query.assert_called_once()
    service.event_rpc.update.assert_called()


def test_when_revealing_votes_for_non_existing_story_should_cause_an_error(db_session):
    # arrange
    fake_sid = '1aaa'
    fake_poker_id1 = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_event_id1 = uuid.uuid4()
    fake_event_id2 = uuid.uuid4()
    fake_participant_id1 = uuid.uuid4()
    fake_participant_id2 = uuid.uuid4()

    def fake_event_query(*args, **kwargs):
        return {
            "items": [
                {
                    "id": str(fake_event_id1),
                    "type": "vote",
                    "content": "5",
                    "revealed": False,
                    "creator": str(fake_participant_id1),
                    "storyId": str(fake_story_id1)
                },
                {
                    "id": str(fake_event_id2),
                    "type": "vote",
                    "content": "2",
                    "revealed": False,
                    "creator": str(fake_participant_id1),
                    "storyId": str(fake_story_id1)
                }
            ]
        }

    def fake_event_update(*args, **kwargs):
        return {
            "id": str(fake_event_id1),
            "type": "vote",
            "content": "5",
            "revealed": True,
            "creator": str(fake_participant_id1),
            "storyId": str(fake_story_id1)
        }

    service = worker_factory(StoryService, db=db_session)
    service.event_rpc.query.side_effect = fake_event_query
    service.event_rpc.update.side_effect = fake_event_update
    service.gateway_rpc.broadcast.side_effect = lambda *args, **kwargs: None
    service.dispatch.side_effect = lambda *args, **kwargs: None

    # act
    # assert
    with pytest.raises(NotFound):
        result = service.reveal(fake_sid, str(fake_story_id1))
