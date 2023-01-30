from pydantic import BaseSettings, Field


class Config(BaseSettings):
    FLASK_ENV: str = 'production'
    DB_HOST: str = Field('db', env='POSTGRES_HOST')
    DB_NAME: str = Field('auth_database', env='POSTGRES_DB')
    DB_USER: str = Field('root', env='POSTGRES_USER')
    DB_PASSWORD: str = Field('root', env='POSTGRES_PASSWORD')

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return 'postgresql://{0}:{1}@{2}/{3}'.format(
            self.DB_USER,
            self.DB_PASSWORD,
            self.DB_HOST,
            self.DB_NAME,
        )

    REDIS_HOST: str = Field('localhost', env='REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='REDIS_PORT')
    TOKEN_ACCESS_TTL: int = 600  # in seconds
    TOKEN_REFRESH_TTL: int = 604800  # in seconds
    SWAGGER: dict = {
        'title': 'Swagger JWT Authentiation App',
        'uiversion': 3,
        'doc_dir': './api/docs/',
    }
    JAEGER_HOST: str = Field('jaeger', env='JAEGER_HOST')
    JAEGER_PORT: int = Field(6831, env='JAEGER_PORT')
    DISABLE_AUTHORIZATION: bool = False
    RATELIMIT_DEFAULT: str = '1000 per minute'
    # no authorization required to get access to this api enpoints
    SKIP_AUTHORIZATION: tuple = (
        'v1.auth.login',
        'v1.auth.refresh',
        'v1.oauth.login',
        'v1.users.create',
    )

    SECRET_KEY: str = Field(..., env='SECRET_KEY')
    TOKEN_SECRET_KEY: str = Field(..., env='TOKEN_SECRET_KEY')


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    FLASK_ENV: str = 'development'
    SECRET_KEY: str = 'flask_secret_key'
    DISABLE_AUTHORIZATION: bool = True


class TestingConfig(DevelopmentConfig):
    TESTING: bool = True
    RATELIMIT_DEFAULT: str = '20 per minute'
    TOKEN_SECRET_KEY: str = 'secret_key_for_token_encoding'
