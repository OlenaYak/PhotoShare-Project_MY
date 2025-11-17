"""merge heads

Revision ID: 8b44753867c6
Revises: 349e9074af9e, 884726d93566
Create Date: 2025-11-16 19:11:21.192117

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b44753867c6'
down_revision: Union[str, Sequence[str], None] = ('349e9074af9e', '884726d93566')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
