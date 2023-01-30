"""The service won't handle errors itself, API does it."""
import random

from models import UserRoleModel
from models.user import UserModel
from pbkdf2 import crypt
from services import RoleService
from services.exceptions import ObjectNotFoundException


def random_string(length):
    def random_char():
        return chr(random.randint(ord('a'), ord('z')))

    return ''.join(random_char() for _ in range(length))


class UserService:
    password_hash_iterations = 100

    def __init__(self, db, role_service: RoleService):
        self.db = db
        self.role_service = role_service

    def create(self, login, password, oauth=None, commit=True) -> UserModel:
        """We hash the password here.
        :returns: Success or not"""
        hashed_password = crypt(
            password,
            '.' + random_string(random.randint(10, 20)),
            iterations=self.password_hash_iterations,
        )
        new_user = UserModel(login=login, password=hashed_password)
        if oauth:
            oauth.user = new_user
        self.db.session.add(new_user)
        if commit:
            self.db.session.commit()
        return new_user

    def get(self, user_id) -> UserModel:
        obj = UserModel.query.get(user_id)
        if not obj:
            raise ObjectNotFoundException('User', user_id)
        return obj

    def get_by_yandex(self, yandex_id) -> UserModel:
        return UserModel.query.filter(UserModel.yandex_id == yandex_id).one_or_none()

    def all(self) -> list[UserModel]:
        return UserModel.query.all()

    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if user:
            self.db.session.delete(user)
            self.db.session.commit()
            return True
        return False

    def get_by_credentials(self, login, password) -> UserModel:
        user = UserModel.query.filter(UserModel.login == login).one_or_none()
        if user and user.password == crypt(password, user.password):
            return user

    def change_password(self, user, new_password):
        hashed_password = crypt(
            new_password,
            '.' + random_string(random.randint(10, 20)),
            iterations=self.password_hash_iterations,
        )
        user.password = hashed_password
        self.db.session.commit()

    def assign_role(self, user_id, role_id):
        self.get(user_id)  # Check that the user exists
        self.role_service.get(role_id)  # Check that the role exists
        user_role = UserRoleModel.get(user_id=user_id, role_id=role_id)
        self.db.session.add(user_role)
        # user_obj.roles.append(role_obj) <- doesn't work
        self.db.session.commit()

    def revoke_role(self, user_id, role_id):
        user_role = UserRoleModel.query.filter_by(
            user_id=user_id, role_id=role_id
        ).all()
        if user_role:
            for itm in user_role:
                self.db.session.delete(itm)
        else:
            raise ObjectNotFoundException('Role for user', role_id)
