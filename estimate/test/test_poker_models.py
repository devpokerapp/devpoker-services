import pytest
import uuid
from sqlalchemy.exc import IntegrityError
from nameko_sqlalchemy.database import Session
from poker.models import Poker
from story.models import Story


def test_creating_poker_should_fill_id_field(db_session: Session):
    # arrange
    poker = Poker(creator='')

    # act
    db_session.add(poker)
    db_session.commit()

    # assert
    assert hasattr(poker, 'id')
    assert poker.id is not None
    assert type(poker.id) is uuid.UUID


def test_creating_poker_should_fill_vote_pattern(db_session: Session):
    # arrange
    poker = Poker(creator='')

    # act
    db_session.add(poker)
    db_session.commit()

    # assert
    assert hasattr(poker, 'id')
    assert poker.id is not None
    assert type(poker.id) is uuid.UUID
    assert type(poker.vote_pattern) is str
    assert poker.vote_pattern == "0,1,2,3,5,8,13,?,__coffee"


def test_creating_poker_without_creator_should_cause_error(db_session: Session):
    # arrange
    poker = Poker()
    db_session.add(poker)

    # act
    # assert
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_when_reading_poker_stories_should_include_stories_ordered_by_order_value(db_session):
    # arrange
    fake_poker_id = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_story_id2 = uuid.uuid4()

    poker = Poker(id=fake_poker_id, creator='user@test.com')
    db_session.add(poker)
    db_session.commit()

    db_session.add(Story(id=fake_story_id1, name="Story 1", poker_id=fake_poker_id, order=1))
    db_session.add(Story(id=fake_story_id2, name="Story 1", poker_id=fake_poker_id, order=2))
    db_session.commit()

    # act
    stories = poker.stories

    # assert
    assert len(stories) == 2
    assert type(stories[0]) is Story
    assert type(stories[1]) is Story
    assert stories[0].order == 1
    assert stories[1].order == 2
