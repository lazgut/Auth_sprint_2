from marshmallow import (
    EXCLUDE,
    Schema,
    ValidationError,
    fields,
    validates_schema,
)


class AuthSchema(Schema):
    @validates_schema
    def required_data(self, data, **kwargs):
        """This validator checks if the child schema provides required data"""
        if set(data.keys()) != {'access_token'}:
            raise ValidationError(
                'Children schemas must provide "access_token" property'
            )


class DataSchema(Schema):
    @validates_schema
    def required_data(self, data, **kwargs):
        """This validator checks if the child schema provides required data"""
        if set(data.keys()) != {'login', 'id'}:
            raise ValidationError(
                'Children schemas must provide "id", "login" properties'
            )


class AccessTokenSchema(AuthSchema):
    class Meta:
        unknown = EXCLUDE

    access_token = fields.String(required=True)


class LoginIdSchema(DataSchema):
    """Yandex response data
    {
        "login": "vasya",
        "old_social_login": "uid-mmzxrnry",
        "default_email": "test@yandex.ru",
        "id": "1000034426",
        "client_id": "4760187d81bc4b7799476b42b5103713",
        "emails": [
            "test@yandex.ru",
            "other-test@yandex.ru"
        ],
        "openid_identities": [
            "http://openid.yandex.ru/vasya/",
            "http://vasya.ya.ru/"
        ],
        "psuid": "1.AAceCw.tbHgw5DtJ9_zeqPrk-Ba2w.qPWSRC5v2t2IaksPJgnge"
    }

    Github response data
    {
        "login": "octocat",
        "id": 1,
        ...
        "email": "octocat@github.com",
        ...
    }
    """

    class Meta:
        unknown = EXCLUDE

    login = fields.String(required=True)
    id = fields.Integer(required=True)
