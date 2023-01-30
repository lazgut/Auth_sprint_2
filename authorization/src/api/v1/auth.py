from datetime import datetime
from http import HTTPStatus

import jwt
from app import auth_service, history_service, user_service
from flasgger.utils import swag_from
from flask import Blueprint, current_app, request
from marshmallow.exceptions import ValidationError
from schemas import UserData

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['POST'])
@swag_from('../docs/auth_login.yml', methods=['Post'])
def login():
    try:
        login_data = UserData().load(request.get_json())
    except ValidationError as err:
        return err.messages, HTTPStatus.BAD_REQUEST

    user = user_service.get_by_credentials(**login_data)
    if user is None:
        return {'message': 'Wrong credentials'}, HTTPStatus.FORBIDDEN

    tokens = auth_service.gen_tokens(user)
    history_service.store_history(user.id, request)

    return tokens, HTTPStatus.OK


@bp.route('/refresh', methods=['POST'])
@swag_from('../docs/refresh.yml', methods=['Post'])
def token_refresh():
    data = request.get_json()
    token = data.get('refresh')
    response = current_app.extensions['redis'].get('refresh:{0}'.format(token))

    if response:
        current_app.extensions['redis'].delete('refresh:{0}'.format(token))
        user_data = jwt.decode(
            token,
            current_app.config['TOKEN_SECRET_KEY'],
            algorithms='HS256',
        )
        user = user_service.get(user_data['id'])
        if user:
            tokens = auth_service.gen_tokens(user)
            return tokens, HTTPStatus.OK

    return '', HTTPStatus.FORBIDDEN


@bp.route('/logout', methods=['POST'])
@swag_from('../docs/logout.yml', methods=['Post'])
def logout():
    tokens = request.get_json()
    response = current_app.extensions['redis'].get(
        'refresh:{0}'.format(tokens['refresh'])
    )

    if response:
        current_app.extensions['redis'].delete('refresh:{0}'.format(tokens['refresh']))
        current_app.extensions['redis'].set(
            'invalidated_access:{0}'.format(tokens['access']),
            0,
            ex=current_app.config['TOKEN_ACCESS_TTL'],
        )

        return '', HTTPStatus.OK

    return '', HTTPStatus.NO_CONTENT


@bp.route('/logout-all', methods=['POST'])
@swag_from('../docs/logout_all.yml', methods=['Post'])
def logout_all():
    tokens = request.get_json()
    user_data = jwt.decode(
        tokens['refresh'], current_app.config['TOKEN_SECRET_KEY'], algorithms='HS256'
    )
    time_now = datetime.timestamp(datetime.now())
    current_app.extensions['redis'].set(
        'logout_all: {0}'.format(user_data['id']),
        time_now,
        ex=current_app.config['TOKEN_REFRESH_TTL'],
    )
    return '', HTTPStatus.OK


@bp.route('/access-check', methods=['POST'])
@swag_from('../docs/access_check.yml', methods=['Post'])
def access_token_check():
    data = request.get_json()
    token = data.get('access')

    roles = auth_service.token_roles(token)
    if roles:
        return {'valid_roles': roles}

    return '', HTTPStatus.FORBIDDEN
