"""add vote pattern to poker table

Revision ID: 4d925f1e51b9
Revises: b63997518279
Create Date: 2023-12-10 12:34:34.014448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4d925f1e51b9'
down_revision: Union[str, None] = 'b63997518279'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pokers",
                  sa.Column("vote_pattern", sa.String(), nullable=False, server_default="0,1,2,3,5,8,13,?,__coffee"))


def downgrade() -> None:
    op.drop_column("pokers", "vote_pattern")
