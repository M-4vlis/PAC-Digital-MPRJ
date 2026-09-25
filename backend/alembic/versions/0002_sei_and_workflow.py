"""SEI staging fields and workflow linkage"""
revision = "0002"
down_revision = "0001"
from alembic import op
import sqlalchemy as sa

def upgrade():
    with op.batch_alter_table("demands") as batch:
        batch.add_column(sa.Column("sei_process_number", sa.String(40), nullable=True))
        batch.add_column(sa.Column("sei_protocol_id", sa.String(80), nullable=True))
        batch.add_column(sa.Column("sei_status", sa.String(30), nullable=False, server_default="not_linked"))
        batch.create_index("ix_demands_sei_process_number", ["sei_process_number"], unique=False)

def downgrade():
    with op.batch_alter_table("demands") as batch:
        batch.drop_index("ix_demands_sei_process_number")
        batch.drop_column("sei_status")
        batch.drop_column("sei_protocol_id")
        batch.drop_column("sei_process_number")
