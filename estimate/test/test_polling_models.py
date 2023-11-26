import uuid

import pytest
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
    
    polling = Polling(story_id=fake_story_id)
    
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
