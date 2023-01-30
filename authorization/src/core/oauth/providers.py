from abc import ABC, abstractmethod
from enum import Enum

import requests
from core.oauth.schemas import (
    AccessTokenSchema,
    AuthSchema,
    DataSchema,
    LoginIdSchema,
)
from marshmallow import Schema


class OauthProviders(Enum):
    yandex = 'yandex'
    github = 'github'


class BaseProvider(ABC):
    def __init__(self):
        self.auth_schema = self._auth_data_schema()
        if not isinstance(self.auth_schema, AuthSchema):
            raise NotImplementedError(
                'Auth data schema must be a child of {0}'.format(AuthSchema.__class__)
            )
        self.data_schema = self._user_data_schema()
        if not isinstance(self.data_schema, DataSchema):
            raise NotImplementedError(
                'User data schema must be a child of {0}'.format(DataSchema.__class__)
            )

    @abstractmethod
    def _auth_data_schema(self) -> Schema:
        """Returns marshmallow schema object to parse and validate user info data"""
        raise NotImplementedError

    @abstractmethod
    def _user_data_schema(self) -> Schema:
        """Returns marshmallow schema object to parse and validate user info data"""
        raise NotImplementedError

    @abstractmethod
    def _user_data_url(self) -> str:
        """Oauth api url which provides an user data"""
        raise NotImplementedError

    @abstractmethod
    def name(self) -> str:
        """Return short provider name as a string"""
        raise NotImplementedError

    def user_data(self, auth_data: str) -> dict:
        access_token = self.auth_schema.load(auth_data)['access_token']
        user_data = requests.get(
            self._user_data_url(),
            headers={'Authorization': 'Bearer {0}'.format(access_token)},
        )
        return self.data_schema.load(user_data.json())


class YandexProvider(BaseProvider):
    def _auth_data_schema(self) -> AuthSchema:
        return AccessTokenSchema()

    def _user_data_schema(self) -> DataSchema:
        return LoginIdSchema()

    def _user_data_url(self) -> str:
        return 'https://login.yandex.ru/info'

    def name(self) -> str:
        return OauthProviders.yandex.value


class GithubProvider(BaseProvider):
    def _auth_data_schema(self) -> AuthSchema:
        return AccessTokenSchema()

    def _user_data_schema(self) -> DataSchema:
        return LoginIdSchema()

    def _user_data_url(self) -> str:
        return 'https://api.github.com/user'

    def name(self) -> str:
        return OauthProviders.github.value
