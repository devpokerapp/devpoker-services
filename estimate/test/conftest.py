import pytest
from sqlalchemy import create_engine
from base.models import DeclarativeBase

# MODELS:
from poker.models import Poker
from story.models import Story
from event.models import Event
from participant.models import Participant
from polling.models import Polling
from vote.models import Vote
from invite.models import Invite


@pytest.fixture(scope='session')
def db_url():
    """Overriding db_url fixture from `nameko_sqlalchemy`

    `db_url` and `model_base` below are used by `db_session` fixture
    from `nameko_sqlalchemy`.

    `db_session` fixture is used for any database dependent tests.

    For more information see: https://github.com/onefinestay/nameko-sqlalchemy
    """
    return 'sqlite:///:memory:'


@pytest.fixture(scope="session")
def model_base():
    """Overriding model_base fixture from `nameko_sqlalchemy`"""
    return DeclarativeBase


@pytest.fixture(scope='session')
def db_connection(db_url, model_base, db_engine_options):
    engine = create_engine(db_url, **db_engine_options)
    model_base.metadata.create_all(bind=engine)
    connection = engine.connect()
    model_base.metadata.bind = engine

    yield connection

    # fixes missing "bind=" on nameko-sqlalchemy
    model_base.metadata.drop_all(bind=engine)
    engine.dispose()
