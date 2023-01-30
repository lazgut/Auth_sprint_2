import uuid

from core.oauth.providers import OauthProviders
from db import db
from sqlalchemy.dialects.postgresql import UUID


class OauthModel(db.Model):
    """Keep user's oauth data"""

    __tablename__ = 'oauth'
    __table_args__ = (
        db.UniqueConstraint('remote_id', 'provider', name='remoteid_provider'),
    )

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    provider = db.Column(db.Enum(OauthProviders))
    remote_id = db.Column(db.String(128))
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE')
    )
    user = db.relationship('UserModel', back_populates='oauth')
