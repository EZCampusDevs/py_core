"""Add user table

Revision ID: a592f1d77399
Revises: 064dea6f0f88
Create Date: 2023-10-08 21:48:31.723761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a592f1d77399'
down_revision: Union[str, None] = '064dea6f0f88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

fk = 'tbl_word_course_data_ibfk_1'

def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(fk, 'tbl_word_course_data', type_='foreignkey')
    op.create_foreign_key(fk, 'tbl_word_course_data', 'tbl_word', ['word_id'], ['word_id'], ondelete='CASCADE')
    op.create_table(
        "tbl_user",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.VARCHAR(length=128), nullable=False),
        sa.Column("email", sa.VARCHAR(length=128)),
        sa.Column("password_hash", sa.BINARY(length=60), nullable=False),
        sa.Column("is_suspended", sa.Boolean(), nullable=False),
        sa.Column("account_status", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.sql.func.now()),
        sa.PrimaryKeyConstraint("user_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("tbl_user")
    op.drop_constraint(fk, 'tbl_word_course_data', type_='foreignkey')
    op.create_foreign_key(fk, 'tbl_word_course_data', 'tbl_course_data', ['course_data_id'], ['course_data_id'])
    # ### end Alembic commands ###
