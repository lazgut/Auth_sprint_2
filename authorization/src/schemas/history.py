from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from models.history import HistoryModel


class HistoryData(SQLAlchemyAutoSchema):
    class Meta:
        model = HistoryModel
        exclude = ('id',)
