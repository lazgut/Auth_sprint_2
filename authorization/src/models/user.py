import uuid

from db import db
from sqlalchemy.dialects.postgresql import UUID


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    login = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    oauth = db.relationship('OauthModel', back_populates='user')

    def __repr__(self):
        return f'<User {self.login}>'
