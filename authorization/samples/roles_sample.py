"""An example to use roles and resources."""
import datetime

from app import user_service
from db import db
from flask import Flask
from models import UserRoleModel
from models.resource import ResourceModel
from models.resource_role import ResourceRoleModel
from models.role import RoleModel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://app:app@localhost/auth'

db.init_app(app)
app.app_context().push()


# from schemas.resource import ResourceData  # <- to execute 'permission' set

random_mark = str(datetime.datetime.now())

client_service_id = 'ddfsd' + random_mark
role1 = RoleModel(name='role1' + random_mark, client_service_id=client_service_id)
role2 = RoleModel(name='role2' + random_mark, client_service_id=client_service_id)

db.session.add(role1)
db.session.add(role2)
db.session.commit()  # <- don't forget it to get id-s for the roles

res = ResourceModel(name='resource1')
db.session.add(res)
p1 = ResourceRoleModel(resource=res, role_id=role1.id, action='VIEW')
p2 = ResourceRoleModel(resource=res, role_id=role2.id, action='DELETE')
db.session.add(p1)
db.session.add(p2)
db.session.commit()


user = user_service.create('Ivan' + random_mark, '123')
ur1 = UserRoleModel(user_id=user.id, role_id=role1.id)
ur2 = UserRoleModel(user_id=user.id, role_id=role2.id)
db.session.add(ur1)
db.session.add(ur2)
db.session.commit()
print(user.user_role)
print(role1.user_role)
print(role2.user_role)

# region check user rights
roles_to_resource_and_action = ResourceRoleModel.query.filter_by(
    resource_id=res.id, action='VIEW'
)
# ^ Here are roles for resource and action
permission_record = UserRoleModel.query.filter_by(user_id=user.id)
# ^ Here are roles for the user
resource_roles_set = set(res_role.role_id for res_role in roles_to_resource_and_action)
user_role_set = set(user_role.role_id for user_role in permission_record)
print(resource_roles_set & user_role_set)
# endregion
