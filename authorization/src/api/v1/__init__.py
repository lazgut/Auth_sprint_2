from api.v1.auth import bp as auth_bp
from api.v1.oauth import bp as oauth_bp
from api.v1.role import bp as roles_bp
from api.v1.users import bp as users_bp
from app import auth_service
from flask import Blueprint, current_app, request

bp = Blueprint('v1', __name__, url_prefix='/v1')

bp.register_blueprint(auth_bp)
bp.register_blueprint(oauth_bp)
bp.register_blueprint(users_bp)
bp.register_blueprint(roles_bp)


@bp.before_request
def check_request_id():
    if current_app.config['TESTING']:
        return
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        raise RuntimeError('request id is required')


@bp.before_request
def check_authorization():
    # disable authorization in test env
    if current_app.config['DISABLE_AUTHORIZATION']:
        return
    if request.endpoint in current_app.config['SKIP_AUTHORIZATION']:
        return
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer'):
        token = auth_header[7:]
        roles = auth_service.token_roles(token)
        if 'admin' in roles:
            return

    return {'message': 'Access restricted'}, 403
