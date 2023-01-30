import uuid

from db import db
from models.actions import UserActions
from .resource import ResourceModel
from .role import RoleModel  # ok
from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import UUID


class ResourceRoleModel(db.Model):
    """Links resource and role and action"""

    __tablename__ = 'resource_role_table'

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    resource_id = db.Column(UUID(as_uuid=True), db.ForeignKey('resources.id'))

    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('roles.id'))

    action = db.Column(Enum(UserActions), name='resource_action')

    resource = db.relationship(ResourceModel, backref='permission')
    role = db.relationship(RoleModel, backref='permission')
