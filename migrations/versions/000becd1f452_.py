"""empty message

Revision ID: 000becd1f452
Revises: 1443878ad537
Create Date: 2018-07-12 11:18:55.673012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '000becd1f452'
down_revision = '1443878ad537'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('agreement', 'document')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('agreement', sa.Column('document', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
