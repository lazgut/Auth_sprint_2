from http import HTTPStatus

import pytest

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio


async def test_login_wrong_data(make_request):
    response = await make_request('post')('auth/login', json={'login': 'test_user'})

    assert response.status == HTTPStatus.BAD_REQUEST
    assert 'password' in response.body


async def test_login_not_exists(make_request):
    response = await make_request('post')(
        'auth/login', json={'login': 'test_user', 'password': 'test_pass'}
    )

    assert response.status == HTTPStatus.FORBIDDEN
    assert response.body == {'message': 'Wrong credentials'}


async def test_login(make_request, user_fixture):
    response = await make_request('post')(
        'auth/login', json={'login': 'test_user', 'password': 'test_pass'}
    )

    assert response.status == HTTPStatus.OK
    assert set(response.body.keys()) == set(['access', 'refresh'])


async def test_token_refresh(make_request, user_fixture):
    response_login = await make_request('post')(
        'auth/login', json={'login': 'test_user', 'password': 'test_pass'}
    )
    tokens = response_login.body
    response_refresh = await make_request('post')(
        'auth/refresh', json={'refresh': tokens['refresh']}
    )
    assert response_refresh.status == HTTPStatus.OK
    assert set(response_refresh.body.keys()) == set(['access', 'refresh'])


async def test_token_refresh_not_exists(make_request, fake_token):
    response = await make_request('post')('auth/refresh', json={'refresh': fake_token})
    assert response.status == HTTPStatus.FORBIDDEN
