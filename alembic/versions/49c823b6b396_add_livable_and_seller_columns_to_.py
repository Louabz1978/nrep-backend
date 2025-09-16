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
    op.add_column("properties", sa.Column("livable", sa.Boolean(), nullable=True, server_default=sa.sql.expression.true()))

    op.create_table(
        "property_owners",
        sa.Column("property_id", sa.Integer(), sa.ForeignKey("properties.property_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("seller_id", sa.Integer(), sa.ForeignKey("consumers.consumer_id", ondelete="CASCADE"), primary_key=True),
    )

    op.drop_column("properties", "owner_id")


def downgrade():
    op.drop_table("property_owners")

    op.drop_column("properties", "livable")

    op.add_column(
        "properties",
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=False)
    )
    