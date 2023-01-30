from http import HTTPStatus

import pytest

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio


async def test_ratelimit(make_request, role_fixture):
    response = await make_request('get')('roles')
    # normal response here
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)

    # make more then config.TestingConfig['RATELIMIT_DEFAULT'] requests
    for i in range(21):
        response = await make_request('get')('roles')
    assert response.status == HTTPStatus.TOO_MANY_REQUESTS
