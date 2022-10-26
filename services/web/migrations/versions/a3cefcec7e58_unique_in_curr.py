"""unique in curr

Revision ID: a3cefcec7e58
Revises: 9541084431a3
Create Date: 2022-10-25 14:31:24.329598

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3cefcec7e58'
down_revision = '9541084431a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'currency_pair', ['pair'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'currency_pair', type_='unique')
    # ### end Alembic commands ###