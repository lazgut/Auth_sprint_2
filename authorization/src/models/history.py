import datetime
import uuid

import architect
from config import Config
from db import db
from sqlalchemy.dialects.postgresql import UUID


@architect.install(
    'partition',
    type='range',
    subtype='date',
    constraint='year',
    column='access_date',
    orm='sqlalchemy',
    db=Config().SQLALCHEMY_DATABASE_URI,
)
class HistoryModel(db.Model):
    __tablename__ = 'access_history'

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    device = db.Column(db.String(255), nullable=False)
    access_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE')
    )
