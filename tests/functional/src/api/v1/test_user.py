import re
from http import HTTPStatus
from uuid import uuid4

import pytest

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio

USER_ID = None


async def test_user_create(make_request):
    response = await make_request('post')(
        'users',
        json={'login': 'test_user', 'password': 'test_pass'},
    )
    location_regex = (
        '.*/v1/users/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$'
    )
    location = re.match(location_regex, response.headers['location'])

    assert response.status == HTTPStatus.CREATED

    # The URI of the new resource is included in the Location header of the response.
    assert location is not None, '"{0}" doesn\'t match location regex "{1}"'.format(
        response.headers['location'],
        location_regex,
    )

    # The response body contains a representation of the resource.
    assert response.body['login'] == 'test_user'

    # Ensure we don't expose password
    assert response.body.keys() == {'id', 'login'}

    # assign user's id to global variable to use in another tests
    # this is intentionally below assertions
    global USER_ID
    USER_ID = location.group(1)


async def test_user_read_notexists(make_request):
    response = await make_request('get')('users/{0}'.format(str(uuid4())))
    assert response.status == HTTPStatus.NOT_FOUND


async def test_user_read(make_request):
    global USER_ID
    response = await make_request('get')('users/{0}'.format(USER_ID))
    assert response.status == HTTPStatus.OK
    assert response.body['id'] == USER_ID


# This test relies on test before it.
async def test_users_read(make_request):
    response = await make_request('get')('users')
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert response.body[0]['id'] == USER_ID


async def test_create_existing_user(make_request):
    await make_request('post')(
        'users',
        json={'login': 'test_user1', 'password': 'test_pass'},
    )

    response = await make_request('post')(
        'users',
        json={'login': 'test_user1', 'password': 'test_pass'},
    )
    assert response.status == HTTPStatus.INTERNAL_SERVER_ERROR


async def test_get_user_history(make_request):
    await make_request('post')(
        'auth/login', json={'login': 'test_user', 'password': 'test_pass'}
    )
    r = await make_request('get')('users/{0}/history'.format(USER_ID))
    assert r.status == HTTPStatus.OK
    assert r.body[0].keys() == set(['access_date', 'device'])


async def test_history_by_not_exists_user_id(make_request):
    r = await make_request('get')('users/{0}/history'.format(uuid4()))
    assert r.status == HTTPStatus.NOT_FOUND


async def test_user_remove_exist(make_request):
    r = await make_request('delete')('users/{0}'.format(USER_ID))
    assert r.status == HTTPStatus.OK


async def test_user_remove_not_exist(make_request):
    r = await make_request('delete')('users/{0}'.format(USER_ID))
    assert r.status == HTTPStatus.NOT_FOUND
