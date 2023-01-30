import redis


class RedisExtension:
    pool: None

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.logger.info(
            'Connecting to redis at %s:%d ...',
            app.config['REDIS_HOST'],
            app.config['REDIS_PORT'],
        )
        self.pool = redis.ConnectionPool(
            host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT']
        )
        app.logger.info('Connected to redis')

        app.extensions['redis'] = self

    @property
    def connection(self):
        conn = redis.StrictRedis(connection_pool=self.pool)
        conn.set_response_callback('*', lambda x: x.decode() if x else x)
        return conn

    def __getattr__(self, attr):
        return getattr(self.connection, attr)
