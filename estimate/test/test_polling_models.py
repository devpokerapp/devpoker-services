import uuid

import pytest
from sqlalchemy.orm import Session

from polling.models import Polling
from poker.models import Poker
from story.models import Story


def test_creating_polling_should_fill_completion_flags(db_session):
    # arrange
    fake_poker_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()
    db_session.add(Story(id=fake_story_id, name="Story 1", poker_id=fake_poker_id))
    db_session.commit()
    
    polling = Polling(story_id=fake_story_id, poker_id=fake_poker_id)
    
    # act
    db_session.add(polling)
    db_session.commit()

    # assert
    assert hasattr(polling, 'id')
    assert hasattr(polling, 'created_at')
    assert hasattr(polling, 'updated_at')
    assert hasattr(polling, 'completed')
    assert hasattr(polling, 'revealed')
    assert polling.id is not None
    assert type(polling.id) is uuid.UUID
    assert polling.completed is False
    assert polling.revealed is False


def test_deleting_story_should_delete_all_its_pollings(db_session: Session):
    # arrange
    fake_poker_id = uuid.uuid4()
    fake_story_id = uuid.uuid4()
    fake_polling_id1 = uuid.uuid4()
    fake_polling_id2 = uuid.uuid4()

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()

    story = Story(id=fake_story_id, name="Story 1", poker_id=fake_poker_id)
    db_session.add(story)
    db_session.commit()

    polling1 = Polling(id=fake_polling_id1, story_id=fake_story_id, poker_id=fake_poker_id)
    polling2 = Polling(id=fake_polling_id2, story_id=fake_story_id, poker_id=fake_poker_id)
    db_session.add(polling1)
    db_session.add(polling2)
    db_session.commit()

    # act
    db_session.delete(story)
    db_session.commit()

    result = db_session.query(Polling)\
        .filter(Polling.id == fake_polling_id1)\
        .first()

    # assert
    assert result is None

