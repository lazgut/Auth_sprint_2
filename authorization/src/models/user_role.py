import uuid

from db import db
from .role import RoleModel
from .user import UserModel
from sqlalchemy.dialects.postgresql import UUID


class UserRoleModel(db.Model):
    """Links resource and role and action"""

    __tablename__ = 'user_role_table'

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))

    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('roles.id'))
    __table_args__ = (db.Index('user_role_index', 'user_id', 'role_id'),)

    user = db.relationship(UserModel, backref='user_role')
    role = db.relationship(RoleModel, backref='user_role')
