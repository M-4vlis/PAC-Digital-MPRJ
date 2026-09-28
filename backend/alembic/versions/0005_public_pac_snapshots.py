"""Public PAC snapshots"""
revision = "0005"
down_revision = "0004"
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table("public_pac_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="published"),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("year", "version", name="uq_public_pac_snapshot_year_version"),
    )
    op.create_index("ix_public_pac_snapshots_year", "public_pac_snapshots", ["year"])
    op.create_index("ix_public_pac_snapshots_content_hash", "public_pac_snapshots", ["content_hash"])


def downgrade():
    op.drop_index("ix_public_pac_snapshots_content_hash", table_name="public_pac_snapshots")
    op.drop_index("ix_public_pac_snapshots_year", table_name="public_pac_snapshots")
    op.drop_table("public_pac_snapshots")
