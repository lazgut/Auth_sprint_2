from http import HTTPStatus

from app import role_service
from flasgger.utils import swag_from
from flask import Blueprint, make_response, request, url_for
from schemas import RoleData
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint('roles', __name__, url_prefix='/roles')


@bp.route('', methods=['GET'])
@swag_from('../docs/get_role.yml', methods=['Get'])
def get_roles():
    return role_service.all()


@bp.route('', methods=['POST'])
@swag_from('../docs/create_role.yml', methods=['Post'])
def create():
    try:
        data = request.get_json()
        role_name = data['role_name']
        client_id = data['client_service_id']
        role_obj = role_service.create(role_name, client_id)
    except SQLAlchemyError as e:
        return {'message': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    response = make_response(role_obj, HTTPStatus.CREATED)
    response.location = url_for('.get_role', role_id=role_obj.id, _external=True)
    return response


@bp.route('/<role_id>', methods=['PUT'])
@swag_from('../docs/update_role.yml', methods=['Put'])
def update_role(role_id):
    role_data = RoleData().load(request.get_json())
    # Don't allow to change role id
    if str(role_data['id']) != role_id:
        return {'message': 'ID change is restricted'}, HTTPStatus.BAD_REQUEST
    role_service.update(**role_data)
    return '', HTTPStatus.NO_CONTENT


@bp.route('/<role_id>', methods=['GET'])
def get_role(role_id):
    role = role_service.get(role_id)
    if role is None:
        return '', HTTPStatus.NOT_FOUND
    else:
        return role, HTTPStatus.OK


@bp.route('/delete/<role_id>', methods=['DELETE'])
@swag_from('../docs/delete_role.yml', methods=['Delete'])
def delete(role_id):
    result = role_service.delete(role_id)
    if result:
        return {'message': f'Role with id {role_id} deleted'}, HTTPStatus.OK
    else:
        return {
            'message': f'Role with id {role_id} not deleted, something went wrong'
        }, HTTPStatus.INTERNAL_SERVER_ERROR


@bp.route('/check/<action>/<user_id>/<resource_id>', methods=['GET'])
@swag_from('../docs/check_role.yml', methods=['Get'])
def check(action, user_id, resource_id):
    result = role_service.check_user_rights(user_id, resource_id, action.upper())
    if result:
        return {'message': 'Access granted'}, HTTPStatus.OK
    return {'message': 'Access denied'}, HTTPStatus.FORBIDDEN
