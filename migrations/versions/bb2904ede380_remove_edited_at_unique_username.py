"""remove edited at, unique username

Revision ID: bb2904ede380
Revises: c5bfdc59d5d1
Create Date: 2023-10-15 18:16:14.758897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb2904ede380'
down_revision: Union[str, None] = 'c5bfdc59d5d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

c_name = "_username_unique_constraint"

def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tbl_user', 'edited_at')
    op.create_unique_constraint(c_name, "tbl_user", ["username"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(c_name, 'tbl_user', type_='unique')
    op.add_column('tbl_user', sa.Column('edited_at', sa.TIMESTAMP(), server_default=sa.sql.func.now(), onupdate=sa.sql.func.now(), nullable=True))
    # ### end Alembic commands ###
