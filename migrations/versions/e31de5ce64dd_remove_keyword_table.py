"""remove keyword table

Revision ID: e31de5ce64dd
Revises: 0b7a406ddf09
Create Date: 2025-01-04 14:32:17.126844

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e31de5ce64dd'
down_revision = '0b7a406ddf09'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_keywords_id', table_name='keywords')
    op.drop_table('keywords')
    op.drop_column('users', 'query')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('query', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.create_table(
        'keywords',
        sa.Column(
            'created_at',
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            'updated_at',
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column('id', sa.UUID(), autoincrement=False, nullable=True),
        sa.Column(
            'mode',
            postgresql.ENUM('binding', 'optional', 'negative', name='keywordmodes'),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('user_id', sa.BIGINT(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='keywords_user_id_fkey'),
        sa.PrimaryKeyConstraint('name', 'user_id', name='keywords_pkey'),
    )
    op.create_index('ix_keywords_id', 'keywords', ['id'], unique=False)
    # ### end Alembic commands ###
