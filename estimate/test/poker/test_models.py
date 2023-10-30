import pytest
import uuid
from nameko_sqlalchemy.database import Session
from poker.models import Poker
from story.models import Story


def test_creating_event_should_contain_id(db_session: Session):
    # arrange
    poker = Poker(creator='')

    # act
    db_session.add(poker)
    db_session.commit()

    # assert
    assert hasattr(poker, 'id')
    assert poker.id is not None
    assert type(poker.id) is uuid.UUID
