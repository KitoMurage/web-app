"""Add is_default column to workout_plans

Revision ID: 791dfbff47aa
Revises: 
Create Date: 2024-12-03 16:39:06.485875

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '791dfbff47aa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add the 'is_default' column to the 'workout_plans' table
    with op.batch_alter_table('workout_plans', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_default', sa.BOOLEAN(), nullable=True))


def downgrade():
    # Drop the 'is_default' column from the 'workout_plans' table
    with op.batch_alter_table('workout_plans', schema=None) as batch_op:
        batch_op.drop_column('is_default')
