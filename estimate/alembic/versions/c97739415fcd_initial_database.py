"""Initial database

Revision ID: c97739415fcd
Revises: 
Create Date: 2023-10-29 11:44:46.158405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c97739415fcd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pokers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("creator", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "stories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("value", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("pokers", sa.Column("current_story_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_pokers_current_story_id",
        "pokers",
        "stories",
        ["current_story_id"],
        ["id"]
    )

    op.add_column("stories", sa.Column("poker_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(
        "fk_stories_poker_id",
        "stories",
        "pokers",
        ["poker_id"],
        ["id"]
    )

    op.create_table(
        "events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("creator", sa.String(), nullable=False),
        sa.Column("revealed", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("events", sa.Column("story_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(
        "fk_events_story_id",
        "events",
        "stories",
        ["story_id"],
        ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_events_current_story_id", "events")
    op.drop_table("events")

    op.drop_constraint("fk_stories_poker_id", "stories")
    op.drop_constraint("fk_pokers_current_story_id", "pokers")
    op.drop_table("stories")

    op.drop_table("pokers")
