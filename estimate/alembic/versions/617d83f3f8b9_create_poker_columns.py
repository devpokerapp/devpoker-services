"""create poker columns

Revision ID: 617d83f3f8b9
Revises: f697c632a221
Create Date: 2024-03-20 23:17:27.306684

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '617d83f3f8b9'
down_revision: Union[str, None] = 'f697c632a221'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pollings", sa.Column("poker_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(
        "fk_pollings_poker_id",
        "pollings",
        "pokers",
        ["poker_id"],
        ["id"]
    )
    op.add_column("events", sa.Column("poker_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(
        "fk_events_poker_id",
        "events",
        "pokers",
        ["poker_id"],
        ["id"]
    )
    op.add_column("votes", sa.Column("poker_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(
        "fk_votes_poker_id",
        "votes",
        "pokers",
        ["poker_id"],
        ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_participants_poker_id", "participants")
    op.drop_constraint("fk_events_poker_id", "events")
    op.drop_constraint("fk_votes_poker_id", "votes")
