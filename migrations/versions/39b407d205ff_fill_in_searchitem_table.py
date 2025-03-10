"""fill in searchitem table

Revision ID: 39b407d205ff
Revises: bcfedcd90fa6
Create Date: 2025-01-18 23:33:32.370900

"""

import sqlalchemy as sa
from alembic import op

from bot import models

# revision identifiers, used by Alembic.
revision = '39b407d205ff'
down_revision = 'bcfedcd90fa6'


def upgrade() -> None:
    """Create searchitem objects for existing users."""
    bind = op.get_bind()
    query = sa.select(models.User.__table__)
    users = bind.execute(query).all()
    searchitems = [
        {
            'user_id': user.id,
            'grade': user.grade.lower(),
            'language': 'python',
        }
        for user in users
    ]
    bind.execute(sa.insert(models.SearchItem.__table__), searchitems)


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.delete(models.SearchItem.__table__))
