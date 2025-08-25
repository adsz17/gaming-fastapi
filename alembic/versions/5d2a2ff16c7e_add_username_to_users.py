"""add username column to users"""

from alembic import op
import sqlalchemy as sa

revision = "5d2a2ff16c7e"
down_revision = "366efed92ee6"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('users', sa.Column('username', sa.String(length=50), nullable=False, server_default=''))
    if op.get_bind().dialect.name != "sqlite":
        op.alter_column('users', 'username', server_default=None)

def downgrade() -> None:
    op.drop_column('users', 'username')
