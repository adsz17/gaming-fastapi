"""add wallet and transaction tables and is_admin"""

from alembic import op
import sqlalchemy as sa


revision = "a5781473f094"
down_revision = "5d2a2ff16c7e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"),
    )
    if op.get_bind().dialect.name != "sqlite":
        op.alter_column("users", "is_admin", server_default=None)

    op.create_table(
        "wallets",
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("balance", sa.Numeric(18, 6), nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "ttype",
            sa.Enum(
                "deposit",
                "withdraw",
                "bet",
                "win",
                "adjustment",
                name="transaction_type",
            ),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(18, 6), nullable=False),
        sa.Column(
            "round_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            sa.ForeignKey("rounds.id"),
            nullable=True,
        ),
        sa.Column("op_id", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("op_id"),
    )
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_transactions_user_id", table_name="transactions")
    op.drop_table("transactions")
    op.drop_table("wallets")
    op.drop_column("users", "is_admin")
