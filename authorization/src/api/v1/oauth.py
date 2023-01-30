from http import HTTPStatus

from app import auth_service
from core.oauth.exceptions import AuthProviderNotExists
from flask import Blueprint, request

bp = Blueprint('oauth', __name__, url_prefix='/oauth')


@bp.route('/login/<provider>', methods=['POST'])
def login(provider):
    """This endpoint gets fragment data
    that was send from yandex oauth and parsed on frontend.

    eg.
        access_token=<новый OAuth-токен>
        & expires_in=<время жизни токена в секундах>
        & token_type=bearer
        [& state=<значение параметра state в запросе>]
        [& scope=<права доступа>]

    or from github
    eg.
        access_token=gho_16C7e42F292c6912E7710c838347Ae178B4a
        &token_type=bearer
        &scope=repo%2Cgist
    """
    try:
        tokens = auth_service.oauth_login(provider, request)
    except AuthProviderNotExists:
        return 'OAuth provider "{0}" not exists'.format(provider), HTTPStatus.NOT_FOUND

    return tokens, HTTPStatus.OK
