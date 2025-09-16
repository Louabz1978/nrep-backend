"""Add livable and seller columns to properties

Revision ID: 49c823b6b396
Revises: 
Create Date: 2025-09-16 10:00:47.916045

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49c823b6b396'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # --- Add new column livable to properties table ---
    op.add_column("properties", sa.Column("livable", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()))

    # --- Drop owner_id from properties table ---
    op.drop_column("properties", "owner_id")

def downgrade():
    op.drop_column("properties", "livable")

    op.add_column(
        "properties",
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=False, server_default=sa.text("1"))
    )
