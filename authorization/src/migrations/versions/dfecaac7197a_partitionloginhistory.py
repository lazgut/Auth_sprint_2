"""Partition login history

Revision ID: dfecaac7197a
Revises: 154e3ebf4251
Create Date: 2022-12-21 20:28:22.668709

"""
from architect.commands.partition import run as run_partition

# revision identifiers, used by Alembic.
revision = 'dfecaac7197a'
down_revision = '154e3ebf4251'
branch_labels = None
depends_on = None


def upgrade():
    run_partition({'module': 'models.history'})


def downgrade():
    pass
