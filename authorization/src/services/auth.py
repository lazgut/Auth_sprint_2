import secrets
import string
from datetime import datetime, timedelta

import jwt
from core.oauth.exceptions import AuthProviderNotExists
from core.oauth.providers import OauthProviders
from flask import Request
from models.oauth import OauthModel
from models.user import UserModel
from schemas import UserData


class AuthService:
    config: None  # app config
    redis: None  # redis connection

    def __init__(self, db, history_service, user_service, oauth_providers: list):
        self.db = db
        self.history_service = history_service
        self.oauth_providers = {i.name(): i for i in oauth_providers}
        self.user_service = user_service

    def init_app(self, app):
        self.config = app.config
        self.redis = app.extensions['redis']

    def oauth_login(self, provider: str, request: Request):
        """
        then send request to yandex api to get user info in the format:

        """

        try:
            oauth_provider = self.oauth_providers[provider]
        except KeyError:
            raise AuthProviderNotExists
        user_data = oauth_provider.user_data(request.get_json())
        oauth_user = OauthModel.query.filter(
            OauthModel.provider == getattr(OauthProviders, provider),
            OauthModel.remote_id == str(user_data['id']),
        ).one_or_none()

        if oauth_user:
            user = oauth_user.user
        else:
            # register the user if this is first time login
            # don't try to match existing user by email because it's not secure

            # generate password for user
            password = ''.join(
                secrets.choice(string.ascii_letters + string.digits) for i in range(16)
            )

            oauth = OauthModel(
                provider=getattr(OauthProviders, provider),
                remote_id=str(user_data['id']),
            )
            self.db.session.add(oauth)
            user = self.user_service.create(user_data['login'], password, oauth)

        # generate auth api tokens for user
        tokens = self.gen_tokens(user)

        # write login history
        self.history_service.store_history(user.id, request)

        return tokens

    def gen_tokens(self, user: UserModel):
        tokens = {
            'access': self._gen_access(user, self.config['TOKEN_REFRESH_TTL']),
            'refresh': self._gen_refresh(user),
        }
        self.redis.set(
            'refresh:{0}'.format(tokens['refresh']),
            1,
            ex=self.config['TOKEN_REFRESH_TTL'],
        )
        return tokens

    def token_roles(self, token):
        """Check access token for validity and get roles from it"""
        user_data = jwt.decode(
            token,
            self.config['TOKEN_SECRET_KEY'],
            algorithms='HS256',
        )

        time_now = int(datetime.timestamp(datetime.now()))
        token_exp = int(user_data['exp'])
        is_invalidated = self.redis.get('invalidated_access:{0}'.format(token))
        is_logout_all = self.redis.get('logout_all: {0}'.format(user_data['id']))

        if is_logout_all:
            logout_all_time = float(is_logout_all)
            token_iat = int(user_data['iat'])
            if (
                logout_all_time < token_iat
                and time_now < token_exp
                and not is_invalidated
            ):
                return user_data.get('roles', [])
        elif time_now < token_exp and not is_invalidated:
            return user_data.get('roles', [])

    def _gen_access(self, user: UserModel, ttl: int) -> str:
        time_now = datetime.now()
        payload = UserData().dump(user)
        payload.update(
            {
                'exp': time_now + timedelta(seconds=ttl),
                'iat': time_now,
            }
        )
        payload['roles'] = [i.role.name for i in user.user_role]
        return jwt.encode(
            payload,
            self.config['TOKEN_SECRET_KEY'],
            algorithm='HS256',
        )

    def _gen_refresh(self, user: UserModel) -> str:
        return self._gen_access(user, self.config['TOKEN_REFRESH_TTL'])
