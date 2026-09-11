"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-08-19

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("admin", "investigator", name="userrole"), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
    )

    # wallets
    op.create_table(
        "wallets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("address", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("blockchain", sa.String(50), nullable=False),
        sa.Column("label", sa.String(255), nullable=True),
        sa.Column("tx_count", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("balance", sa.Float(), server_default=sa.text("0.0"), nullable=True),
        sa.Column("first_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_active", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_blacklisted", sa.Boolean(), server_default=sa.text("0"), nullable=True),
        sa.Column("fraud_score", sa.Float(), nullable=True),
        sa.Column("risk_level", sa.String(20), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )

    # transactions
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tx_hash", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("sender_address", sa.String(255), nullable=False, index=True),
        sa.Column("receiver_address", sa.String(255), nullable=False, index=True),
        sa.Column("blockchain", sa.String(50), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("amount_usd", sa.Float(), nullable=True),
        sa.Column("gas_fee", sa.Float(), nullable=True),
        sa.Column("gas_fee_usd", sa.Float(), nullable=True),
        sa.Column("token", sa.String(50), server_default="NATIVE", nullable=True),
        sa.Column("block_number", sa.BigInteger(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), server_default="confirmed", nullable=True),
        sa.Column("is_flagged", sa.Boolean(), server_default=sa.text("0"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )

    # wallet_features
    op.create_table(
        "wallet_features",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("wallet_address", sa.String(255), nullable=False, index=True),
        sa.Column("blockchain", sa.String(50), nullable=True),
        sa.Column("incoming_tx", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("outgoing_tx", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("avg_tx_amount", sa.Float(), server_default=sa.text("0.0"), nullable=True),
        sa.Column("max_tx_amount", sa.Float(), server_default=sa.text("0.0"), nullable=True),
        sa.Column("balance", sa.Float(), server_default=sa.text("0.0"), nullable=True),
        sa.Column("active_days", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("gas_usage", sa.Float(), server_default=sa.text("0.0"), nullable=True),
        sa.Column("token_diversity", sa.Integer(), server_default=sa.text("1"), nullable=True),
        sa.Column("neighbor_count", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("degree_centrality", sa.Float(), server_default=sa.text("0.0"), nullable=True),
        sa.Column("betweenness_centrality", sa.Float(), server_default=sa.text("0.0"), nullable=True),
        sa.Column("pagerank", sa.Float(), server_default=sa.text("0.0"), nullable=True),
        sa.Column("clustering_coefficient", sa.Float(), server_default=sa.text("0.0"), nullable=True),
        sa.Column("cross_chain_tx_count", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )

    # predictions
    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("wallet_address", sa.String(255), nullable=False, index=True),
        sa.Column("fraud_score", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(20), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(50), server_default="mock-v1.0", nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )

    # wallet_categories
    op.create_table(
        "wallet_categories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("wallet_address", sa.String(255), nullable=False, index=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(50), server_default="mock-v1.0", nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )

    # investigations
    op.create_table(
        "investigations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum("open", "in_progress", "closed", "archived", name="investigationstatus"), nullable=True),
        sa.Column("priority", sa.String(20), server_default="medium", nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True, index=True),
        sa.Column("assigned_to_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # investigation_wallets
    op.create_table(
        "investigation_wallets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("investigation_id", sa.Integer(), sa.ForeignKey("investigations.id"), nullable=True, index=True),
        sa.Column("wallet_address", sa.String(255), nullable=False),
        sa.Column("blockchain", sa.String(50), nullable=True),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )

    # investigation_notes
    op.create_table(
        "investigation_notes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("investigation_id", sa.Integer(), sa.ForeignKey("investigations.id"), nullable=True, index=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )

    # blacklist
    op.create_table(
        "blacklist",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("address", sa.String(255), nullable=False, index=True),
        sa.Column("blockchain", sa.String(50), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("confidence", sa.String(20), server_default="high", nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=True),
        sa.Column("added_by", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # notifications
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=True, index=True),
        sa.Column("type", sa.String(100), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("is_read", sa.Boolean(), server_default=sa.text("0"), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )

    # blockchain_configs
    op.create_table(
        "blockchain_configs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("blockchain", sa.String(50), nullable=False, unique=True),
        sa.Column("display_name", sa.String(100), nullable=True),
        sa.Column("api_url", sa.String(500), nullable=True),
        sa.Column("api_key_encrypted", sa.String(500), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.text("1"), nullable=True),
        sa.Column("last_sync", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tx_count", sa.BigInteger(), server_default=sa.text("0"), nullable=True),
        sa.Column("wallet_count", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("block_height", sa.BigInteger(), server_default=sa.text("0"), nullable=True),
        sa.Column("sync_status", sa.String(50), server_default="idle", nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("blockchain_configs")
    op.drop_table("notifications")
    op.drop_table("blacklist")
    op.drop_table("investigation_notes")
    op.drop_table("investigation_wallets")
    op.drop_table("investigations")
    op.drop_table("wallet_categories")
    op.drop_table("predictions")
    op.drop_table("wallet_features")
    op.drop_table("transactions")
    op.drop_table("wallets")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS investigationstatus")
