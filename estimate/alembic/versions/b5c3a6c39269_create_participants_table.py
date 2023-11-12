"""Create participants table

Revision ID: b5c3a6c39269
Revises: c97739415fcd
Create Date: 2023-11-11 19:35:18.873908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5c3a6c39269'
down_revision: Union[str, None] = 'c97739415fcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "participants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("sid", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("participants", sa.Column("poker_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(
        "fk_participants_poker_id",
        "participants",
        "pokers",
        ["poker_id"],
        ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_participants_poker_id", "participants")
    op.drop_table("participants")
