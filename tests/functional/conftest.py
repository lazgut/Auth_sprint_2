import asyncio
import secrets
from dataclasses import dataclass
from typing import AsyncGenerator, Optional

import aiohttp
import aiopg
import aioredis
import pytest
import pytest_asyncio
from settings import Settings

SETTINGS = Settings()


@dataclass
class HTTPResponse:
    body: dict
    status: int
    headers: dict


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='module')
async def pg_connection() -> AsyncGenerator[aiopg.connection.Connection, None]:
    connection_kwargs = {
        'dbname': SETTINGS.pg_db,
        'user': SETTINGS.pg_user,
        'password': SETTINGS.pg_password,
        'host': SETTINGS.pg_host,
        'port': SETTINGS.pg_port,
    }
    async with aiopg.create_pool(**connection_kwargs) as pool:
        async with pool.acquire() as conn:

            yield conn

            async with conn.cursor() as cur:
                await cur.execute(('TRUNCATE users CASCADE;' 'TRUNCATE roles CASCADE;'))


@pytest_asyncio.fixture(scope='module')
async def redis() -> AsyncGenerator[aiopg.connection.Connection, None]:
    redis_table = aioredis.Redis(host=SETTINGS.redis_host, port=SETTINGS.redis_port)

    yield redis_table

    await redis_table.flushall()


@pytest_asyncio.fixture(scope='module')
async def session(pg_connection, redis):
    session = aiohttp.ClientSession(headers={'Cache-Control': 'no-store'})

    yield session

    await session.close()


@pytest_asyncio.fixture(scope='module')
def make_request(session):
    """Helper to make api requests"""

    def wrapper(type: str = 'get'):
        async def inner(
            method: str, json: Optional[dict] = None, headers: Optional[dict] = None
        ) -> HTTPResponse:
            url = 'http://{0}:{1}/v1/{2}'.format(
                SETTINGS.api_host,
                SETTINGS.api_port,
                method,
            )
            async with getattr(session, type)(
                url, json=json, headers=headers
            ) as response:
                try:
                    body = await response.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    body = await response.text()
                return HTTPResponse(
                    body=body,
                    status=response.status,
                    headers=response.headers,
                )

        return inner

    return wrapper


@pytest_asyncio.fixture
async def user_fixture(make_request):
    response = await make_request('post')(
        'users',
        json={'login': 'test_user', 'password': 'test_pass'},
    )
    yield response.body
    await make_request('delete')('users/{0}'.format(response.body['id']))


@pytest_asyncio.fixture
async def role_fixture(make_request):
    response = await make_request('post')(
        'roles',
        json={'role_name': 'test_role', 'client_service_id': 'test_client_id'},
    )
    yield response.body
    await make_request('delete')('roles/delete/{0}'.format(response.body['id']))


@pytest.fixture
def fake_token():
    return secrets.token_hex(32)
