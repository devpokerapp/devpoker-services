"""add order to story table

Revision ID: 86842d3596d3
Revises: a63bc6e4150a
Create Date: 2024-03-31 18:41:14.221769

"""
import datetime

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86842d3596d3'
down_revision: Union[str, None] = 'a63bc6e4150a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("stories", sa.Column("order", sa.Integer(), nullable=False,
                                       default=sa.select(sa.func.count()).select_from(sa.table('stories'))))


def downgrade() -> None:
    op.drop_column("stories", "order")
