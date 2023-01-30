"""init_roles

Revision ID: 912bc0b24fd0
Revises: 3f8e0286450e
Create Date: 2022-12-16 12:13:55.298162

"""
from uuid import uuid4
from alembic import op


# revision identifiers, used by Alembic.
from sqlalchemy import MetaData, Table

revision = '912bc0b24fd0'
down_revision = '3f8e0286450e'
branch_labels = None
depends_on = None


def upgrade():
    def create_roles():
        meta = MetaData(bind=op.get_bind())
        meta.reflect(only=('roles',))
        roles_table = Table('roles', meta)
        op.bulk_insert(roles_table,
                       [
                           {'id': str(uuid4()), 'name': 'admin'},
                           {'id': str(uuid4()), 'name': 'user'},
                       ]
                       )
    create_roles()


def downgrade():
    # TODO How to delete data?
    pass
