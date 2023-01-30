from logging.config import dictConfig
from os import environ

from core.flask import Flask
from core.oauth.providers import GithubProvider, YandexProvider
from core.trace import configure_tracer, request_hook
from db import db
from ext.redis import RedisExtension
from flasgger import Swagger
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from services import (  # noqa
    AuthService,
    HistoryService,
    RoleService,
    UserService,
)
from werkzeug.utils import import_string

redis = RedisExtension()
history_service = HistoryService(db)
role_service = RoleService(db)
user_service = UserService(db, role_service)
auth_service = AuthService(
    db, history_service, user_service, [GithubProvider(), YandexProvider()]
)


def create_app():
    # import it here to avoid circular import
    # as an alternative use app.g for services access
    from api.v1 import bp

    app = Flask(__name__)
    # instantiate config class
    # to skip execution of SECRET_KEY related code at compile time
    cfg = import_string(environ.get('AUTH_CONFIG', 'config.ProductionConfig'))()
    app.config.from_object(cfg)

    if not app.config['TESTING']:
        configure_tracer(app.config['JAEGER_HOST'], app.config['JAEGER_PORT'])
        FlaskInstrumentor().instrument_app(app, request_hook=request_hook)

    db.init_app(app)

    Migrate(app, db)
    if app.config['TESTING']:
        from flask_migrate import upgrade

        with app.app_context():
            upgrade()

    redis.init_app(app)
    auth_service.init_app(app)
    Marshmallow(app)
    app.register_blueprint(bp)

    Limiter(
        app,
        key_func=get_remote_address,
        storage_uri='redis://',
        storage_options={'connection_pool': app.extensions['redis'].pool},
    )

    Swagger(
        app,
        template={
            'swagger': '2.0',
            'info': {
                'title': 'Auth service',
                'version': '1.0',
            },
            'consumes': [
                'application/json',
            ],
            'produces': [
                'application/json',
            ],
        },
    )

    dictConfig(
        {
            'version': 1,
            'formatters': {
                'default': {
                    'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
                }
            },
            'handlers': {
                'wsgi': {
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                    'formatter': 'default',
                }
            },
            'root': {'level': 'INFO', 'handlers': ['wsgi']},
        }
    )

    return app
