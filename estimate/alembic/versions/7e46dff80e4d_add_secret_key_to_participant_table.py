"""add secret key to participant table

Revision ID: 7e46dff80e4d
Revises: 617d83f3f8b9
Create Date: 2024-03-24 18:30:54.593145

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e46dff80e4d'
down_revision: Union[str, None] = '617d83f3f8b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("participants", sa.Column("secret_key", sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column("participants", "secret_key")
