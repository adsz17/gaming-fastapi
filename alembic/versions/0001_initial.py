"""initial tables"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "accounts",
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("balance", sa.Numeric(18, 6), server_default="0", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "rounds",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("game_code", sa.String(length=50), server_default="crash_v1", nullable=False),
        sa.Column("bet", sa.Numeric(18, 6), nullable=False),
        sa.Column("payout", sa.Numeric(18, 6), server_default="0", nullable=False),
        sa.Column("server_seed_hash", sa.Text, nullable=False),
        sa.Column("client_seed", sa.Text, nullable=False),
        sa.Column("nonce", sa.BigInteger(), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_rounds_user_id", "rounds", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_rounds_user_id", table_name="rounds")
    op.drop_table("rounds")
    op.drop_table("accounts")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
