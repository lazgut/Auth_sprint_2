from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from models.role import RoleModel


class RoleData(SQLAlchemyAutoSchema):
    class Meta:
        model = RoleModel
