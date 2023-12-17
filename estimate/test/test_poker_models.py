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
