"""change national_number type

Revision ID: c12035f99cc3
Revises: 49c823b6b396
Create Date: 2025-09-17 23:51:39.318271

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c12035f99cc3'
down_revision: Union[str, Sequence[str], None] = '49c823b6b396'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("consumers") as batch_op:
        batch_op.alter_column(
            "national_number",
            existing_type=sa.Integer(),
            type_=sa.String(length=11),
            existing_nullable=True
        )


def downgrade() -> None:
    with op.batch_alter_table("consumers") as batch_op:
        batch_op.alter_column(
            "national_number",
            existing_type=sa.String(length=20),
            type_=sa.Integer(),
            existing_nullable=True
        )
