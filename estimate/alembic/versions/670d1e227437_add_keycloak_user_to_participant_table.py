"""add keycloak user to participant table

Revision ID: 670d1e227437
Revises: 4d925f1e51b9
Create Date: 2024-01-14 19:43:07.167703

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '670d1e227437'
down_revision: Union[str, None] = '4d925f1e51b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("participants", sa.Column("keycloak_user_id", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("participants", "keycloak_user_id")
