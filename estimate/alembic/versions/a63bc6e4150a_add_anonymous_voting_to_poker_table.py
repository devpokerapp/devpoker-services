"""add anonymous voting to poker table

Revision ID: a63bc6e4150a
Revises: 7e46dff80e4d
Create Date: 2024-03-29 23:34:04.796828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a63bc6e4150a'
down_revision: Union[str, None] = '7e46dff80e4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pokers", sa.Column("anonymous_voting", sa.Boolean(), nullable=False, server_default='false'))
    op.add_column("pollings", sa.Column("anonymous", sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column("pokers", "anonymous_voting")
    op.drop_column("pollings", "anonymous")
