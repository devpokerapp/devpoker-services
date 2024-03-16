"""create invite table

Revision ID: f697c632a221
Revises: 670d1e227437
Create Date: 2024-03-15 23:40:18.559964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f697c632a221'
down_revision: Union[str, None] = '670d1e227437'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "invites",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("invites", sa.Column("poker_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(
        "fk_invites_poker_id",
        "invites",
        "pokers",
        ["poker_id"],
        ["id"]
    )


def downgrade() -> None:
    pass
