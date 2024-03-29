"""Created tbl_event

Revision ID: b0fbe2cf1cd1
Revises: a592f1d77399
Create Date: 2023-10-11 15:53:06.679509

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0fbe2cf1cd1'
down_revision: Union[str, None] = 'a592f1d77399'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "tbl_event",
        sa.Column("event_id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("timezone", sa.VARCHAR(64)),
        sa.Column("name", sa.VARCHAR(512)),
        sa.Column("description", sa.Text()),
        sa.Column("location", sa.VARCHAR(512)),
        sa.Column("seats_filled", sa.Integer()),
        sa.Column("max_capacity", sa.Integer()),
        sa.Column("color", sa.Integer()),
        sa.Column("is_virtual", sa.Boolean()),
        sa.Column("started_at", sa.Date()),
        sa.Column("ended_at", sa.Date()),
        sa.Column("begin_time", sa.VARCHAR(16)),
        sa.Column("end_time", sa.VARCHAR(16)),
        sa.Column("occurrence_unit", sa.Integer()),
        sa.Column("occurrence_interval", sa.Integer()),
        sa.Column("occurrence_repeat", sa.Integer()),
        sa.Column("occurrence_until", sa.Date()),
        sa.Column("days_of_week", sa.Integer()),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("tbl_event")
    # ### end Alembic commands ###
