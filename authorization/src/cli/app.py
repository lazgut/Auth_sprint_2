from getpass import getpass
from uuid import uuid4

import click
from app import create_app, role_service, user_service
from db import db
from models import RoleModel, UserRoleModel
from sqlalchemy.orm.exc import NoResultFound

app = create_app()


@app.cli.command('create-superuser')
@click.argument('login')
def create_superuser(login):
    """The password will be promted"""
    password = getpass('Input password:')

    try:
        admin_role = RoleModel().query.filter_by(name='admin').one()
    except NoResultFound:
        admin_role = role_service.create('admin', 'auth')
    finally:
        db.session.close()

    assert admin_role

    with db.session.begin():
        user = user_service.create(login, password, commit=False)
        user.id = uuid4()
        user_role = UserRoleModel(user_id=user.id, role_id=admin_role.id)
        db.session.add(user_role)
