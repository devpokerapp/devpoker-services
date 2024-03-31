import uuid

from story.models import Story
from poker.models import Poker


def test_when_creating_two_stories_should_have_different_order_values(db_session):
    # arrange
    fake_poker_id = uuid.uuid4()
    fake_story_id1 = uuid.uuid4()
    fake_story_id2 = uuid.uuid4()

    db_session.add(Poker(id=fake_poker_id, creator='user@test.com'))
    db_session.commit()

    story1 = Story(id=fake_story_id1, name="Story 1", poker_id=fake_poker_id)
    story2 = Story(id=fake_story_id2, name="Story 1", poker_id=fake_poker_id)

    # act
    db_session.add(story1)
    db_session.commit()
    db_session.add(story2)
    db_session.commit()

    # assert
    assert story1.order != story2.order

