"""create polling and vote table

Revision ID: b63997518279
Revises: b5c3a6c39269
Create Date: 2023-11-24 22:41:18.162984

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b63997518279'
down_revision: Union[str, None] = 'b5c3a6c39269'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pollings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("value", sa.String(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default='0'),
        sa.Column("revealed", sa.Boolean(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("pollings", sa.Column("story_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(
        "fk_pollings_story_id",
        "pollings",
        "stories",
        ["story_id"],
        ["id"]
    )

    op.create_table(
        "votes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("votes", sa.Column("polling_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(
        "fk_votes_polling_id",
        "votes",
        "pollings",
        ["polling_id"],
        ["id"]
    )

    op.add_column("votes", sa.Column("participant_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(
        "fk_votes_participant_id",
        "votes",
        "participants",
        ["participant_id"],
        ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_votes_participant_id", "votes")
    op.drop_constraint("fk_votes_polling_id", "votes")
    op.drop_table("votes")

    op.drop_constraint("fk_pollings_story_id", "pollings")
    op.drop_table("pollings")
