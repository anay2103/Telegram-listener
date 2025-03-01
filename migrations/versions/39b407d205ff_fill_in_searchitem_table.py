"""fill in searchitem table

Revision ID: 39b407d205ff
Revises: bcfedcd90fa6
Create Date: 2025-01-18 23:33:32.370900

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '39b407d205ff'
down_revision = 'bcfedcd90fa6'


def upgrade() -> None:
    """Create searchitem objects for existing users."""
    bind = op.get_bind()
    users_tbl = sa.Table('users', sa.MetaData(), autoload_with=bind.engine)
    query = sa.select(users_tbl)
    users = bind.execute(query).all()
    searchitems = [
        {
            'user_id': user.id,
            'grade': user.grade.lower(),
            'language': 'python',
        }
        for user in users
    ]
    searchitems_tbl = sa.Table('searchitems', sa.MetaData(), autoload_with=bind.engine)
    bind.execute(sa.insert(searchitems_tbl), searchitems)


def downgrade() -> None:
    bind = op.get_bind()
    searchitems_tbl = sa.Table('searchitems', sa.MetaData(), autoload_with=bind.engine)
    bind.execute(sa.delete(searchitems_tbl))
